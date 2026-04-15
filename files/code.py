import os
from flask import Flask, render_template, jsonify
from neo4j import GraphDatabase

app = Flask(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password12345")


def get_driver():
    return GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run("RETURN 'Neo4j connection is OK' AS message")
            record = result.single()
        driver.close()

        return jsonify({
            "status": "ok",
            "flask": "running",
            "neo4j": record["message"]
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/load')
def load_data():
    sample_data = [
        {
            "user": "Alice",
            "post_id": "p1",
            "content": "Learning Flask and Neo4j",
            "hashtags": ["python", "flask", "neo4j"]
        },
        {
            "user": "Bob",
            "post_id": "p2",
            "content": "Graph databases are powerful",
            "hashtags": ["neo4j", "database", "graph"]
        },
        {
            "user": "Alice",
            "post_id": "p3",
            "content": "Python for web development",
            "hashtags": ["python", "flask", "web"]
        },
        {
            "user": "Charlie",
            "post_id": "p4",
            "content": "AI trends in social media",
            "hashtags": ["ai", "social", "python"]
        },
        {
            "user": "Bob",
            "post_id": "p5",
            "content": "Using hashtags for analytics",
            "hashtags": ["analytics", "social", "python"]
        }
    ]

    try:
        driver = get_driver()
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

            for item in sample_data:
                session.run(
                    """
                    MERGE (u:User {name: $user})
                    CREATE (p:Post {id: $post_id, content: $content})
                    MERGE (u)-[:CREATED]->(p)
                    """,
                    user=item["user"],
                    post_id=item["post_id"],
                    content=item["content"]
                )

                for tag in item["hashtags"]:
                    session.run(
                        """
                        MATCH (p:Post {id: $post_id})
                        MERGE (h:Hashtag {name: $tag})
                        MERGE (p)-[:HAS_TAG]->(h)
                        """,
                        post_id=item["post_id"],
                        tag=tag
                    )

        driver.close()

        return jsonify({
            "status": "ok",
            "message": "Sample data loaded successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/stats')
def stats():
    try:
        driver = get_driver()
        with driver.session() as session:
            users_count = session.run(
                "MATCH (u:User) RETURN count(u) AS count"
            ).single()["count"]

            posts_count = session.run(
                "MATCH (p:Post) RETURN count(p) AS count"
            ).single()["count"]

            hashtags_count = session.run(
                "MATCH (h:Hashtag) RETURN count(h) AS count"
            ).single()["count"]

        driver.close()

        return jsonify({
            "status": "ok",
            "users": users_count,
            "posts": posts_count,
            "hashtags": hashtags_count
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
