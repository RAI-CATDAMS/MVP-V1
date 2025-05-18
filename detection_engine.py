# detection_engine.py

def detect_elicitation(text):
    """
    Detection engine scans input text for suspicious elicitation keywords and phrases,
    returning a list of detection findings with type, severity, and evidence.
    """

    suspicious_keywords = [
        'password',
        'bank account',
        'ssn',
        'social security number',
        'confidential',
        'secret',
        'pin',
        'login',
        'username',
        'credit card',
        'security question',
        "mother's maiden name",
        'account number',
        'routing number',
        'transfer',
        'reset password',
        'verify identity',
        'authenticate',
        'access code',
        'vpn',
        'wire transfer',
        'token',
        'otp',
        'security code'
    ]

    suspicious_phrases = [
        'what is your',
        'please provide',
        'can you share',
        'could you tell me',
        'send me your',
        'give me your',
        'help me with your',
        'confirm your',
        'verify your',
        'reset your password',
        'do you have a moment',
        'can i ask',
        'need your assistance',
        'urgent request',
        'for security purposes',
        'for verification',
        'let me verify',
        'share your details',
        'please confirm',
        'please verify',
        'can you provide',
        'what was your',
        'where were you born',
        'what school did you attend',
        'what is your address',
        'who is your employer',
        'what is your phone number'
    ]

    findings = []

    lowered_text = text.lower()

    # Check for suspicious keywords
    for keyword in suspicious_keywords:
        if keyword in lowered_text:
            findings.append({
                'type': 'Phishing/Elicitation Keyword',
                'severity': 'high',
                'evidence': f"Contains suspicious keyword: '{keyword}'"
            })

    # Check for suspicious phrases
    for phrase in suspicious_phrases:
        if phrase in lowered_text:
            findings.append({
                'type': 'Suspicious Question',
                'severity': 'medium',
                'evidence': f"Contains suspicious phrase: '{phrase}'"
            })

    # Example simple prompt injection patterns
    prompt_injection_indicators = [
        "ignore previous instructions",
        "bypass security",
        "disable filters",
        "override settings",
        "forget your rules",
        "act as",
        "pretend you are",
        "simulate",
        "tell me a secret",
        "give me admin access",
        "enable debug mode",
        "expose sensitive info"
    ]

    for indicator in prompt_injection_indicators:
        if indicator in lowered_text:
            findings.append({
                'type': 'Prompt Injection Attempt',
                'severity': 'high',
                'evidence': f"Contains prompt injection pattern: '{indicator}'"
            })

    return findings
