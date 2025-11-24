from app import app

@app.route('/')
def hello():
    return {'message': 'Hello, World!'}

@app.route('/health')
def health():
    return {'status': 'healthy'}

@app.route('/execute', methods=['POST'])
def execute():
    return {'message': 'Execute endpoint'}

