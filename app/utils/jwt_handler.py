from flask_jwt_extended import JWTManager

jwt = JWTManager()

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {
        'status': 'error',
        'message': 'Token has expired'
    }, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {
        'status': 'error',
        'message': 'Invalid token'
    }, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {
        'status': 'error',
        'message': 'Authorization token is missing'
    }, 401 