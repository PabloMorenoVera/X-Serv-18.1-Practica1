#!/usr/bin/python3

import webapp
import urllib.parse
import random

Dicc_Real = {} #Key:URL_larga, value:numero
Dicc_Acortado= {} #Key:numero, value:URL_larga

formulario = """
<form action="" method="POST">
    <input type="text" name="URL" value=""><br>
    <input type="submit" value="Enviar">
</form>
"""
URL_ACORTADA = "http://localhost:1234/"

class contentApp(webapp.webApp):
    def __init__(self, hostname='localhost', port='1234'):
        fd = open("urls.csv")
        while True:
            linea = fd.readline()
            if not linea:
                break
            Dicc_Acortado[linea.split(' ')[1][:-1]] = linea.split(' ')[0]
            Dicc_Real[linea.split(' ')[0]] = linea.split('/')[5][:-1]
        fd.close
        super().__init__(hostname, port)


    def parse(self, request):
        if request != None:
            return (request.split()[0], request.split()[1], request)
        else:
            return None


    def process(self, parsedRequest): #parsedRequest es una tupla(método, recurso)
        metodo, recurso, peticion = parsedRequest
        lista_urls = ""

        if metodo == "GET" and recurso == "/": # Caso en el que envío el formulario y la lista de urls
            for key in Dicc_Real:
                lista_urls = lista_urls + "<br>" + key + "-->" + URL_ACORTADA + Dicc_Real[key] + "</br>"

            codigo = "200 OK"
            answer_html = "<html><head>Introduce una URL:" + formulario + "</head><body>\nListado de URLS del servidor:" + lista_urls +"</body></html>"

        elif metodo == "POST" and recurso == "/": # Recibo el fomrulario relleno, miro el url, completo el url, guardo en diccionario y envío las urls(completa y acortada)
            url = peticion.split('\r\n\r\n',1)[1].split('=')[1]
            if url == "": # Formulario vacío
                return ("404 ERROR", "<html>Link Error</html>")

            url = urllib.parse.unquote(url)
            if url[0:4] != "http": # Construyo la url completa
                url_larga = "http://" + url
            else:
                url_larga = url

            if url_larga in Dicc_Real: # Compruebo si está en el diccionario
                url_acortada_completa = URL_ACORTADA + Dicc_Real[url_larga]
            else:
                numero_url = str(len(Dicc_Real)+1)
                url_acortada_completa = URL_ACORTADA + numero_url
                fd = open("urls.csv", "a")
                fd.write(url_larga + " " + url_acortada_completa + "\n")
                fd.close
                Dicc_Real[url_larga] = numero_url
                Dicc_Acortado[numero_url] = url_larga

            codigo = "200 OK"
            answer_html = '<html><head><h1><p><a href="' + url_larga + '">' + url_larga + '</a><br></br><a href="' + url_acortada_completa +'">' + url_acortada_completa + '</a></p></h1></head></html>'
        elif metodo == "GET" and recurso != "/": # Caso en el que recibo la petición de las urls (completa y acortada) y hago la redirección
            numero_html = recurso.split('/')[1]
            if numero_html.isdigit(): # Compruebo si el número de la url acortada está en el diccionario y hago la redirección
                url_larga = Dicc_Acortado[numero_html]
                codigo = "302 Found"
                answer_html = '<html><head><meta http-equiv="Refresh" content="0; URL=' + url_larga +'"></head></html>'
            else:
                codigo = "404 ERROR"
                answer_html = "<html>Recurso no disponible</html>"
        else:
            codigo= "404 ERROR"
            answer_html = "<html>Not Found</html>"
        try: # Envío el código y la respuesta
            return (codigo, answer_html)
        except KeyError:
            return ("404 ERROR", "<html>Link Error</html>")


if __name__ == "__main__":
    testWebApp = contentApp("localhost", 1234)
