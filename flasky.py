import sys

from werkzeug.middleware.profiler import ProfilerMiddleware

from app import create_app

if __name__ == "__main__":
    app = create_app('development')
    try:
        restrictions = int(sys.argv[1])
    except(IndexError, TypeError):
        restrictions = 25
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[restrictions])

    app.run(debug=False)
