from flask_jwt_extended import JWTManager

jwt = JWTManager()

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print("[JWT] Token expired")
    return {
        'status': 'error',
        'message': 'Token has expired'
    }, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"[JWT] Invalid token: {error}")
    # 🔧 Better error messaging for debugging
    if "Subject must be a string" in str(error):
        return {
            'status': 'error',
            'message': 'Invalid token: Subject type mismatch - please log out and log in again'
        }, 401
    return {
        'status': 'error',
        'message': 'Invalid token'
    }, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"[JWT] Unauthorized: {error}")
    return {
        'status': 'error',
        'message': 'Authorization token is missing'
    }, 401

# 🔧 Add additional error handlers for better debugging
@jwt.token_verification_failed_loader
def token_verification_failed_callback(jwt_header, jwt_payload):
    print(f"[JWT] Token verification failed")
    return {
        'status': 'error',
        'message': 'Token verification failed'
    }, 401

@jwt.token_verification_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    print(f"[JWT] Token verification check: user_id={jwt_payload.get('sub')}")
    # You can add token blacklist checking here if needed
    return False  # Token is not revoked
