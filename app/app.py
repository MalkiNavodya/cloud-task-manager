from flask import Flask, jsonify, request
import boto3

app = Flask(__name__)

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("cloud-task-manager")


@app.route("/")
def home():
    return jsonify({
        "message": "Cloud Task Manager API is running!"
    })


@app.route("/tasks", methods=["GET"])
def get_tasks():
    response = table.scan()
    return jsonify(response.get("Items", []))


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    response = table.scan(
        ProjectionExpression="id"
    )

    items = response.get("Items", [])

    if items:
        next_id = max(int(item["id"]) for item in items) + 1
    else:
        next_id = 1

    task = {
        "id": next_id,
        "title": data["title"],
        "completed": False
    }

    table.put_item(Item=task)

    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    table.delete_item(
        Key={"id": task_id}
    )

    return jsonify({
        "message": "Task deleted"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
