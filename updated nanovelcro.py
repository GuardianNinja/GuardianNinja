if __name__ == "__main__":
    import argparse, yaml
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    system = NanoVelcroCouplingSystem(
        user_type=cfg["nanovelcro"]["user_type"],
        emergency_password=cfg["nanovelcro"]["emergency_password"],
        biometric_store=cfg["nanovelcro"]["biometric_store"],
        key=cfg["nanovelcro"]["crypto"]["key"],
        gyro_threshold_adult=cfg["nanovelcro"]["thresholds"]["gyro_threshold_adult"],
        gyro_threshold_kid=cfg["nanovelcro"]["thresholds"]["gyro_threshold_kid"],
    )

    # Optional: run a quick self-test
    print("NanoVelcro system loaded and ready.")
