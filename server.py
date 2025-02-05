from flask import Flask, request, jsonify, render_template
from http import HTTPStatus

from reasoning_engine import SaSeoGwanParams, SaSeoGwanLangGraphApp
from utils import SaSeoGwanConfigs

app = Flask(__name__)

# In-memory storage for company profiles
# TODO: In a real application, this would be replaced with a database
companies = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/company", methods=["POST"])
def create_company():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["name", "description", "industry"]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify({"error": f"Missing required field: {field}"}),
                    HTTPStatus.BAD_REQUEST,
                )

        # Create company profile
        company_id = len(companies) + 1
        company_profile = {
            "id": company_id,
            "name": data["name"],
            "description": data["description"],
            "industry": data["industry"],
            "website": data.get("website", ""),  # Optional field
            "contact_email": data.get("contact_email", ""),  # Optional field
        }

        reasoning_engine = SaSeoGwanLangGraphApp(
            project=SaSeoGwanConfigs.project_id,
            location=SaSeoGwanConfigs.location,
            company_params=SaSeoGwanParams(
                company_name=company_profile["name"],
                description=company_profile["description"],
                industry=company_profile["industry"],
                website=company_profile["website"],
                contact_email=company_profile["contact_email"],
            ),
        )
        reasoning_engine.set_up()
        companies[company_id] = {
            "company_profile": company_profile,
            "reasoning_engine": reasoning_engine,
        }

        return (
            jsonify(
                {
                    "message": "Company profile created successfully",
                    "company": company_profile,
                }
            ),
            HTTPStatus.CREATED,
        )

    except Exception as e:
        print(e)
        return (
            jsonify({"error": "Failed to create company profile", "details": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if "message" not in data:
            return (
                jsonify({"error": "Missing message in request"}),
                HTTPStatus.BAD_REQUEST,
            )

        if "company_id" not in data:
            return (
                jsonify({"error": "Missing company_id in request"}),
                HTTPStatus.BAD_REQUEST,
            )

        # Add validation for company_id
        try:
            company_id = int(data["company_id"])
        except ValueError:
            return (
                jsonify({"error": "Invalid company_id format - must be an integer"}),
                HTTPStatus.BAD_REQUEST,
            )

        if company_id not in companies:
            return (
                jsonify({"error": "Company not found"}),
                HTTPStatus.NOT_FOUND,
            )

        company_profile = companies[company_id]["company_profile"]
        reasoning_engine = companies[company_id]["reasoning_engine"]
        response = reasoning_engine.query(data["message"])
        return jsonify({"response": response, "company": company_profile})

    except Exception as e:
        print(e)
        return (
            jsonify({"error": "Chat processing failed", "details": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@app.route("/chat/<int:company_id>")
def chat_interface(company_id):
    if company_id not in companies:
        return "Company not found", 404
    return render_template("chat.html", company=companies[company_id])


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
