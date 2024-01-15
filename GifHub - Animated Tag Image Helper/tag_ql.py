import sqlite3
import requests

# Replace 'C:\\Users\\Stephan\\.stash\\stash-go.sqlite' with the actual path to your SQLite database file
db_path = 'C:\\Users\\Stephan\\.stash\\stash-go.sqlite'

# Connect to the SQLite database using the specified file path
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    while True:
        # Input: Prompt the user to enter the tag name
        tag_name = input("Enter the tag name: ")

        # Execute a SELECT query to retrieve the ID associated with the specified tag name
        cursor.execute("SELECT id FROM tags WHERE name=?", (tag_name,))
        result = cursor.fetchone()

        # Now 'result' contains the ID retrieved from the database for the specified tag name
        if result:
            tag_id = result[0]
            print(f"The ID for the tag '{tag_name}' is: {tag_id}")

            # Prompt the user to enter the image URL
            image_url = input("Enter the image URL: ")

            # Construct the GraphQL mutation string with the provided image URL
            graphql_mutation = f"""
            mutation TagUpdate {{
                tagUpdate(
                    input: {{
                        image: "{image_url}"
                        name: "{tag_name}"
                        id: "{tag_id}"
                    }}
                ) {{
                    image_path
                }}
            }}
            """

            # GraphQL endpoint URL
            graphql_endpoint = "http://192.168.250.197:9999/graphql"

            # Send the GraphQL mutation to the GraphQL endpoint without authentication headers
            response = requests.post(graphql_endpoint, json={'query': graphql_mutation})

            # Check the response
            if response.status_code == 200:
                result_data = response.json()
                print("GraphQL Mutation Result:")
                print(result_data)
            else:
                print(f"Error sending GraphQL mutation. Status Code: {response.status_code}")
                print("Response Text:", response.text)

            break  # Exit the loop if the tag is found

        else:
            print(f"No matching records found for the tag '{tag_name}'.")
            try_another = input("Do you want to try another search term? (yes/no): ").lower()
            if try_another != 'yes':
                break  # Exit the loop if the user doesn't want to try another search term

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    # Close the connection
    conn.close()
