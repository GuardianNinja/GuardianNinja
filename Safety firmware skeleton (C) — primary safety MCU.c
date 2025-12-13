/* safety_supervisor.c
 * Primary safety MCU firmware skeleton
 * - Redundant sensors (primary + secondary)
 * - Cross-checks and heartbeat
 * - Failsafe and emergency descent
 * - Mechanical quick-release control
 * - Signed audit logging (stubbed signing function)
 *
 * NOTE: Replace HAL_* stubs with your platform's HAL/driver calls.
 */

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Configuration */
#define SAMPLE_INTERVAL_MS      50
#define HEARTBEAT_TIMEOUT_MS    1000
#define LOAD_THRESHOLD_KG       50.0f
#define SENSOR_MISMATCH_RATIO   0.20f
#define DROP_RATE_THRESHOLD_KG_PER_S 10.0f

/* Hardware pin placeholders */
#define PIN_MECH_RELEASE        5   // GPIO to trigger mechanical quick-release
#define PIN_DESCENT_ENABLE      6   // GPIO to enable descent actuator
#define PIN_LED_STATUS          13  // status LED

/* Telemetry buffer size */
#define LOG_BUF_SIZE            256

/* Data structures */
typedef struct {
    float load_left;
    float load_right;
    float accel_z;
    uint32_t ts_ms;
} sensor_frame_t;

typedef enum {
    STATE_NORMAL,
    STATE_WARNING,
    STATE_FAILSAFE,
    STATE_EMERGENCY_DESCENT
} system_state_t;

/* Globals */
volatile system_state_t g_state = STATE_NORMAL;
uint32_t g_last_secondary_hb_ms = 0;

/* --- Hardware abstraction stubs (implement for your board) --- */
uint32_t HAL_GetTick_ms(void); /* returns ms since boot */
float HAL_ReadLoadSensor(uint8_t channel); /* channel 0 = left, 1 = right */
float HAL_ReadAccelZ(void);
bool HAL_ReadSecondaryHeartbeat(uint32_t *hb_ts_ms, sensor_frame_t *frame); /* returns true if available */
void HAL_SetGPIO(uint8_t pin, bool value);
void HAL_DelayMs(uint32_t ms);
bool HAL_SignAndStoreLog(const char *json, char *signed_out, size_t out_len); /* sign and persist */

/* --- Utility helpers --- */
static uint32_t now_ms(void) { return HAL_GetTick_ms(); }

static void log_event_json(const char *event_type, const char *reason, const sensor_frame_t *s)
{
    char buf[LOG_BUF_SIZE];
    int n = snprintf(buf, sizeof(buf),
        "{\"ts_ms\":%u,\"node\":\"suit-01\",\"event\":\"%s\",\"reason\":\"%s\",\"loads\":[%.2f,%.2f],\"accel_z\":%.3f}",
        (unsigned)now_ms(), event_type, reason,
        s ? s->load_left : -1.0f, s ? s->load_right : -1.0f, s ? s->accel_z : 0.0f);
    if (n > 0) {
        char signed_blob[LOG_BUF_SIZE + 128];
        if (HAL_SignAndStoreLog(buf, signed_blob, sizeof(signed_blob))) {
            /* Optionally send signed_blob to telemetry uploader */
        } else {
            /* Fallback: store unsigned locally with flag */
        }
    }
}

/* --- Safety actions --- */
static void engage_mechanical_release(bool engaged)
{
    /* engaged = true -> lock; false -> release (example polarity) */
    HAL_SetGPIO(PIN_MECH_RELEASE, engaged);
    log_event_json("MECH_RELEASE", engaged ? "engaged" : "released", NULL);
}

static void enable_descent_mode(void)
{
    HAL_SetGPIO(PIN_DESCENT_ENABLE, true);
    log_event_json("DESCENT", "enabled", NULL);
}

/* --- Checks --- */
static bool sensor_mismatch(const sensor_frame_t *p, const sensor_frame_t *s)
{
    /* Simple relative difference check */
    float pvals[2] = { p->load_left, p->load_right };
    float svals[2] = { s->load_left, s->load_right };
    for (int i = 0; i < 2; ++i) {
        float a = pvals[i], b = svals[i];
        float denom = (a > b ? a : b);
        if (denom < 1.0f) denom = 1.0f; /* avoid divide by zero */
        if (fabsf(a - b) > SENSOR_MISMATCH_RATIO * denom) return true;
    }
    return false;
}

static bool detect_sudden_drop(const sensor_frame_t *prev, const sensor_frame_t *cur)
{
    if (!prev) return false;
    float dt_s = (cur->ts_ms - prev->ts_ms) / 1000.0f;
    if (dt_s <= 0.0f) return false;
    float drop_left = (prev->load_left - cur->load_left) / dt_s;
    float drop_right = (prev->load_right - cur->load_right) / dt_s;
    if (drop_left > DROP_RATE_THRESHOLD_KG_PER_S || drop_right > DROP_RATE_THRESHOLD_KG_PER_S) return true;
    return false;
}

/* --- Main loop --- */
int main(void)
{
    /* Initialization: HAL, sensors, crypto, comms */
    // HAL_Init(); board-specific init here

    sensor_frame_t prev_frame = {0};
    sensor_frame_t primary = {0};
    sensor_frame_t secondary = {0};

    engage_mechanical_release(true); /* start locked for safety */

    while (1) {
        uint32_t loop_start = now_ms();

        /* Read primary sensors */
        primary.load_left  = HAL_ReadLoadSensor(0);
        primary.load_right = HAL_ReadLoadSensor(1);
        primary.accel_z    = HAL_ReadAccelZ();
        primary.ts_ms      = loop_start;

        /* Read secondary (from independent MCU) */
        uint32_t sec_hb_ts = 0;
        bool sec_ok = HAL_ReadSecondaryHeartbeat(&sec_hb_ts, &secondary);
        if (sec_ok) {
            g_last_secondary_hb_ms = sec_hb_ts;
        }

        /* Heartbeat timeout check */
        if ((now_ms() - g_last_secondary_hb_ms) > HEARTBEAT_TIMEOUT_MS) {
            g_state = STATE_FAILSAFE;
            engage_mechanical_release(false);
            log_event_json("FAILSAFE", "secondary_watchdog_timeout", &primary);
            /* notify ops via telemetry uploader (out of scope here) */
            continue;
        }

        /* Redundancy cross-check */
        if (sensor_mismatch(&primary, &secondary)) {
            g_state = STATE_FAILSAFE;
            engage_mechanical_release(false);
            log_event_json("FAILSAFE", "sensor_mismatch", &primary);
            continue;
        }

        /* Overload check */
        if (primary.load_left > LOAD_THRESHOLD_KG || primary.load_right > LOAD_THRESHOLD_KG) {
            g_state = STATE_FAILSAFE;
            engage_mechanical_release(false);
            log_event_json("FAILSAFE", "overload", &primary);
            continue;
        }

        /* Sudden drop detection */
        if (detect_sudden_drop(&prev_frame, &primary)) {
            g_state = STATE_EMERGENCY_DESCENT;
            enable_descent_mode();
            engage_mechanical_release(false);
            log_event_json("EMERGENCY_DESCENT", "sudden_drop_detected", &primary);
            continue;
        }

        /* Normal heartbeat log */
        log_event_json("HEARTBEAT", "ok", &primary);
        g_state = STATE_NORMAL;

        /* Save current as previous for next iteration */
        prev_frame = primary;

        /* Sleep until next sample */
        uint32_t elapsed = now_ms() - loop_start;
        if (elapsed < SAMPLE_INTERVAL_MS) HAL_DelayMs(SAMPLE_INTERVAL_MS - elapsed);
    }

    return 0;
}
