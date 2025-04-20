generators = {}

def register(question_id):
    def decorator(func):
        generators[question_id] = func
        return func
    return decorator