from explora import app
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

app.run(debug=True, port=5000,host='0.0.0.0')
#app.run(debug=True,port=5000,use_reloader=False)
