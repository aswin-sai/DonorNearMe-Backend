from flask_jwt_extended import JWTManager

jwt = JWTManager()

@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return {'message': 'Missing or invalid token'}, 401

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    return {'message': 'Invalid token'}, 401
