from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import platform

app = Flask(__name__)
api = Api(app)

class Welcome(Resource):
	@staticmethod
	def post():
		posted_data = request.get_json()
		name = posted_data['name']
		# print(name)
		# type(name)
		# # returnText = "Hello "+ str(name)
		version = str(platform.python_version())
		return jsonify(
			{'return': version}
		)


api.add_resource(Welcome, '/welcome')
if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')

