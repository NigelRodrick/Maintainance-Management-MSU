"""
Error Handlers
Custom error handlers for HTTP status codes.
"""

from flask import jsonify, render_template


def register_error_handlers(app):
    """Register custom error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        if request_wants_json():
            return jsonify({
                'success': False,
                'error': 'Bad request',
                'message': str(error)
            }), 400
        return render_template('errors/400.html', error=error), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        if request_wants_json():
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Authentication required'
            }), 401
        return render_template('errors/401.html', error=error), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        if request_wants_json():
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Insufficient permissions'
            }), 403
        return render_template('errors/403.html', error=error), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        if request_wants_json():
            return jsonify({
                'success': False,
                'error': 'Not found',
                'message': 'Resource not found'
            }), 404
        return render_template('errors/404.html', error=error), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        if request_wants_json():
            return jsonify({
                'success': False,
                'error': 'Method not allowed',
                'message': 'HTTP method not allowed for this endpoint'
            }), 405
        return render_template('errors/405.html', error=error), 405
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors."""
        if request_wants_json():
            return jsonify({
                'success': False,
                'error': 'Unprocessable entity',
                'message': 'Request data is invalid'
            }), 422
        return render_template('errors/422.html', error=error), 422
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Rate Limit Exceeded errors."""
        if request_wants_json():
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded',
                'message': 'Too many requests, please try again later'
            }), 429
        return render_template('errors/429.html', error=error), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        if request_wants_json():
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'message': 'An unexpected error occurred'
            }), 500
        return render_template('errors/500.html', error=error), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors."""
        if request_wants_json():
            return jsonify({
                'success': False,
                'error': 'Service unavailable',
                'message': 'Service temporarily unavailable'
            }), 503
        return render_template('errors/503.html', error=error), 503


def request_wants_json():
    """Check if the request wants JSON response."""
    from flask import request
    return request.accept_mimetypes['application/json'] >= \
           request.accept_mimetypes['text/html']
