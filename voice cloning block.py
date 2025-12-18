def voice_cloning_guard(requested_voice, user_consent_token):
    # Check consent
    if not validate_consent(user_consent_token, requested_voice):
        raise PermissionError("Voice cloning blocked: no consent provided.")
    
    # Check similarity threshold
    similarity_score = compare_to_real_voice(requested_voice)
    if similarity_score > 0.85:  # adjustable threshold
        raise PermissionError("Voice cloning blocked: too similar to real identity.")
    
    # Add watermark
    cloned_voice = generate_voice(requested_voice)
    return embed_watermark(cloned_voice, system_signature="AI_SAFE")
