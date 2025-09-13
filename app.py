from flask import Flask
app = Flask(__name__)

@app.route("/")
@app.route("/web")
def web():
    return """<!doctype html>
        <html>
           <body>
               <h1>web-сервер на flask</h1>
               <a href="/author">author</a>
           <body>
        <html>"""

@app. route ("/author")
def author() :
    name = "Иванов Иван Иванович"
    group = "ФБИ-00"
    faculty = "ФБ"
    
    return """<!doctype html>
        <html>
            <body>
                <р>Студент: """+ name + """</p> 
                <p>Группа: """ + group + """</p>
                <р>Факультет: """ + faculty + """</p>
                <a href="/web">web</a>
            </body>
        </html>"""
