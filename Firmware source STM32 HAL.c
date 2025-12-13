/* safety_supervisor_stm32.c
 * STM32Cube HAL based safety supervisor for primary MCU
 * - Dual sensor cross-checks
 * - Secondary MCU heartbeat via I2C
 * - Mechanical quick release and descent control via GPIO
 * - Signed audit logs using secure element hook
 * - Two person authorization hook (operator approval)
 *
 * IMPORTANT
 * - Replace SECURE_SIGN and storage hooks with your secure element or TPM implementation
 * - Tune thresholds to your hardware and test extensively with HIL
 */

#include "stm32f4xx_hal.h"
#include <string.h>
#include <stdio.h>
#include <math.h>

/* Configuration constants */
#define SAMPLE_INTERVAL_MS         50U
#define HEARTBEAT_TIMEOUT_MS       1000U
#define LOAD_THRESHOLD_KG          50.0f
#define SENSOR_MISMATCH_RATIO      0.20f
#define DROP_RATE_THRESHOLD_KG_S   10.0f

/* GPIO pins - adapt to your board */
#define PIN_MECH_RELEASE_PORT      GPIOA
#define PIN_MECH_RELEASE_PIN       GPIO_PIN_0
#define PIN_DESCENT_ENABLE_PORT    GPIOA
#define PIN_DESCENT_ENABLE_PIN     GPIO_PIN_1
#define LED_STATUS_PORT            GPIOA
#define LED_STATUS_PIN             GPIO_PIN_5

/* I2C for secondary MCU heartbeat and sensor mirror */
extern I2C_HandleTypeDef hi2c1;

/* Secure element interface prototypes implement in secure module */
bool SECURE_SIGN_AND_STORE(const uint8_t *data, size_t len, uint8_t *signature, size_t *sig_len);
bool SECURE_VERIFY_OPERATOR_APPROVAL(const uint8_t *approval_blob, size_t len);

/* Telemetry uploader hook */
void TELEMETRY_QUEUE_PUSH(const uint8_t *payload, size_t len);

/* ADC read prototypes implement per board */
float ADC_ReadLoadKg(uint8_t channel);
float ACCEL_ReadZ(void);

/* Timing helper */
static inline uint32_t now_ms(void) { return HAL_GetTick(); }

/* Data structures */
typedef struct {
    float load_left;
    float load_right;
    float accel_z;
    uint32_t ts_ms;
} sensor_frame_t;

typedef enum { STATE_NORMAL, STATE_WARNING, STATE_FAILSAFE, STATE_EMERGENCY_DESCENT } system_state_t;

/* Globals */
volatile system_state_t g_state = STATE_NORMAL;
volatile uint32_t g_last_secondary_hb_ms = 0;

/* Logging helper */
static void log_event(const char *event, const char *reason, const sensor_frame_t *s)
{
    char buf[256];
    int n = snprintf(buf, sizeof(buf),
        "{\"ts_ms\":%lu,\"node\":\"suit-01\",\"event\":\"%s\",\"reason\":\"%s\",\"loads\":[%.2f,%.2f],\"accel_z\":%.3f}",
        (unsigned long)now_ms(), event, reason,
        s ? s->load_left : -1.0f, s ? s->load_right : -1.0f, s ? s->accel_z : 0.0f);
    if (n <= 0) return;

    uint8_t signature[256];
    size_t sig_len = 0;
    if (SECURE_SIGN_AND_STORE((uint8_t*)buf, (size_t)n, signature, &sig_len)) {
        /* Build signed payload for telemetry */
        uint8_t payload[512];
        size_t p = 0;
        p += snprintf((char*)payload + p, sizeof(payload) - p, "%s", buf);
        if (sig_len + p < sizeof(payload)) {
            memcpy(payload + p, signature, sig_len);
            p += sig_len;
        }
        TELEMETRY_QUEUE_PUSH(payload, p);
    } else {
        /* Fallback local store or mark unsigned */
        TELEMETRY_QUEUE_PUSH((uint8_t*)buf, (size_t)n);
    }
}

/* Hardware actions */
static void engage_mech_release(bool lock)
{
    HAL_GPIO_WritePin(PIN_MECH_RELEASE_PORT, PIN_MECH_RELEASE_PIN, lock ? GPIO_PIN_SET : GPIO_PIN_RESET);
    log_event("MECH_RELEASE", lock ? "locked" : "released", NULL);
}

static void enable_descent(bool enable)
{
    HAL_GPIO_WritePin(PIN_DESCENT_ENABLE_PORT, PIN_DESCENT_ENABLE_PIN, enable ? GPIO_PIN_SET : GPIO_PIN_RESET);
    log_event("DESCENT", enable ? "enabled" : "disabled", NULL);
}

/* Read secondary MCU via I2C heartbeat and sensor mirror
   Protocol: secondary responds to 0x10 with 16 bytes: ts_ms(4) loadL(float) loadR(float) accelZ(float)
*/
static bool read_secondary(sensor_frame_t *out)
{
    uint8_t cmd = 0x10;
    uint8_t buf[16];
    HAL_StatusTypeDef st = HAL_I2C_Master_Transmit(&hi2c1, (uint16_t)(0x30<<1), &cmd, 1, 50);
    if (st != HAL_OK) return false;
    st = HAL_I2C_Master_Receive(&hi2c1, (uint16_t)(0x30<<1), buf, sizeof(buf), 50);
    if (st != HAL_OK) return false;

    uint32_t ts = (uint32_t)buf[0] | ((uint32_t)buf[1]<<8) | ((uint32_t)buf[2]<<16) | ((uint32_t)buf[3]<<24);
    float l = 0.0f, r = 0.0f, a = 0.0f;
    memcpy(&l, buf+4, 4);
    memcpy(&r, buf+8, 4);
    memcpy(&a, buf+12, 4);
    out->ts_ms = ts;
    out->load_left = l;
    out->load_right = r;
    out->accel_z = a;
    g_last_secondary_hb_ms = now_ms();
    return true;
}

/* Simple mismatch check */
static bool sensor_mismatch(const sensor_frame_t *p, const sensor_frame_t *s)
{
    float pvals[2] = { p->load_left, p->load_right };
    float svals[2] = { s->load_left, s->load_right };
    for (int i = 0; i < 2; ++i) {
        float a = pvals[i], b = svals[i];
        float denom = fmaxf(fabsf(a), fabsf(b));
        if (denom < 1.0f) denom = 1.0f;
        if (fabsf(a - b) > SENSOR_MISMATCH_RATIO * denom) return true;
    }
    return false;
}

/* Sudden drop detection */
static bool detect_sudden_drop(const sensor_frame_t *prev, const sensor_frame_t *cur)
{
    if (!prev) return false;
    float dt = (cur->ts_ms - prev->ts_ms) / 1000.0f;
    if (dt <= 0.0f) return false;
    float dropL = (prev->load_left - cur->load_left) / dt;
    float dropR = (prev->load_right - cur->load_right) / dt;
    return (dropL > DROP_RATE_THRESHOLD_KG_S) || (dropR > DROP_RATE_THRESHOLD_KG_S);
}

/* Two person authorization hook
   Expect approval_blob signed by operator keys and verified by secure element
*/
static bool require_two_person_approval(const uint8_t *approval_blob, size_t len)
{
    return SECURE_VERIFY_OPERATOR_APPROVAL(approval_blob, len);
}

/* Main loop */
void SafetySupervisor_Loop(void)
{
    sensor_frame_t prev = {0};
    sensor_frame_t primary = {0};
    sensor_frame_t secondary = {0};

    engage_mech_release(true); /* start locked */

    while (1) {
        uint32_t t0 = now_ms();

        /* Read primary sensors */
        primary.load_left  = ADC_ReadLoadKg(0);
        primary.load_right = ADC_ReadLoadKg(1);
        primary.accel_z    = ACCEL_ReadZ();
        primary.ts_ms      = t0;

        /* Read secondary */
        bool sec_ok = read_secondary(&secondary);

        /* Heartbeat timeout */
        if (!sec_ok || (now_ms() - g_last_secondary_hb_ms) > HEARTBEAT_TIMEOUT_MS) {
            g_state = STATE_FAILSAFE;
            engage_mech_release(false);
            log_event("FAILSAFE", "secondary_watchdog_timeout", &primary);
            HAL_Delay(100); /* allow telemetry to queue */
            continue;
        }

        /* Redundancy cross-check */
        if (sensor_mismatch(&primary, &secondary)) {
            g_state = STATE_FAILSAFE;
            engage_mech_release(false);
            log_event("FAILSAFE", "sensor_mismatch", &primary);
            HAL_Delay(100);
            continue;
        }

        /* Overload */
        if (primary.load_left > LOAD_THRESHOLD_KG || primary.load_right > LOAD_THRESHOLD_KG) {
            g_state = STATE_FAILSAFE;
            engage_mech_release(false);
            log_event("FAILSAFE", "overload", &primary);
            HAL_Delay(100);
            continue;
        }

        /* Sudden drop */
        if (detect_sudden_drop(&prev, &primary)) {
            g_state = STATE_EMERGENCY_DESCENT;
            enable_descent(true);
            engage_mech_release(false);
            log_event("EMERGENCY_DESCENT", "sudden_drop", &primary);
            HAL_Delay(100);
            continue;
        }

        /* Normal heartbeat */
        log_event("HEARTBEAT", "ok", &primary);
        g_state = STATE_NORMAL;

        prev = primary;

        /* Sleep until next sample */
        uint32_t elapsed = now_ms() - t0;
        if (elapsed < SAMPLE_INTERVAL_MS) HAL_Delay(SAMPLE_INTERVAL_MS - elapsed);
    }
}
