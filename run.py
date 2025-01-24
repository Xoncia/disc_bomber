from app import create_app
import logging
from flask.logging import default_handler
import click

def configure_logging(app):
    """Configure application logging"""
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    default_handler.setFormatter(formatter)
    app.logger.setLevel(logging.INFO)

def print_routes(app):
    """Print all registered routes in a clean format"""
    max_endpoint_length = max(len(rule.endpoint) for rule in app.url_map.iter_rules())
    max_methods_length = max(len(', '.join(rule.methods)) for rule in app.url_map.iter_rules())

    click.echo("\nRegistered Routes:")
    click.echo("-" * (max_endpoint_length + max_methods_length + 45))
    
    for rule in sorted(app.url_map.iter_rules(), key=lambda x: x.endpoint):
        methods = ', '.join(sorted(rule.methods))
        endpoint = rule.endpoint
        path = rule.rule
        
        click.echo(
            f"{endpoint:<{max_endpoint_length}} | "
            f"{methods:<{max_methods_length}} | "
            f"{path}"
        )
    click.echo("-" * (max_endpoint_length + max_methods_length + 45))

app = create_app()
configure_logging(app)

if __name__ == '__main__':
    with app.app_context():
        print_routes(app)
    app.run(debug=True) 