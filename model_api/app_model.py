from flask import Flask, request, jsonify
from model.question_handler import QuestionHandler
from model.document_generator import DocumentGenerator

app = Flask(__name__)
qh = QuestionHandler()
dg = DocumentGenerator()

@app.route("/fetch_questions", methods=["POST"])
def fetch_questions():
    data = request.get_json()
    topic = data.get("topic")
    mode = data.get("mode", "manual")
    num_easy = data.get("num_easy", 3)
    num_medium = data.get("num_medium", 3)
    num_hard = data.get("num_hard", 3)
    
    question_set = qh.get_random_set(topic, num_easy, num_medium, num_hard)
    return jsonify(question_set.to_dict(orient="records"))

@app.route("/generate_doc", methods=["POST"])
def generate_doc():
    data = request.get_json()
    questions = data.get("questions")
    filename = data.get("filename", "outputs/generated_docs/set.docx")
    include_answers = data.get("include_answers", False)
    import pandas as pd
    df = pd.DataFrame(questions)
    dg.export_docx(df, filename, include_answers=include_answers)
    return jsonify({"status":"success", "filename": filename})

if __name__ == "__main__":
    app.run(port=5001, debug=True)
