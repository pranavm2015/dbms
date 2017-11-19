from django.shortcuts import render
import json
import os
from os import environ as env
from sys import argv
from Crypto.Cipher import AES
from django.http import JsonResponse
from django.http import HttpResponse
from py2neo import Graph, authenticate,NodeSelector	
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


graph = Graph("http://neo4j:neo4j@localhost:7474/db/data/", user="neo4j", password="dbms")

def index(request):
	return render (request, "index.html", {})

@csrf_exempt
def student(request):
	if request.method=="GET":
		selector = NodeSelector(graph)
		results = selector.select("professor",research="Big Data")
		cont = {}
		cont["BD"] = [str(row["name"]).replace("{","").replace("}","") for row in results]
		results = selector.select("professor",research="Deep Learning")
		cont["DL"] = [str(row["name"]).replace("{","").replace("}","") for row in results]
		results = selector.select("professor",research="Robotics")
		cont["RB"] = [str(row["name"]).replace("{","").replace("}","") for row in results]
		results = selector.select("professor",research="Embedded Systems")
		cont["ES"] = [str(row["name"]).replace("{","").replace("}","") for row in results]
		results = selector.select("professor",research="Cryptography")
		cont["CP"] = [str(row["name"]).replace("{","").replace("}","") for row in results]
		results = selector.select("professor",research="Algorithms")
		cont["AL"] = [str(row["name"]).replace("{","").replace("}","") for row in results]
		return render (request, "student.html", cont)

	if request.method=="POST":
	    try:
	        form = request.POST
	        print (form)
	        name = form["name"]
	        email = form["email"]
	        ra1 = form["ra1"]
	        ra2 = form["ra2"]
	        ra3 = form["ra3"]
	        pf1 = form["pf1"]
	        pf2 = form["pf2"]
	        pf3 = form["pf3"]
	    except KeyError:
	        return JsonResponse({"respose": "Some error occurred"})
	    else:
	        results = graph.run(
	        "create ("+ name.replace(" ","") +":student{name:" + "\"" + name + "\"" + "," + 
	                            "email:" + "\"" + email + "\"" + "," +
								"ra1:" + "\"" + ra1 + "\"" + "," +
								"ra2:" + "\"" + ra2 + "\"" + "," +
								"ra3:" + "\"" + ra3 + "\"" + "," +	
								"pf1:" + "\"" + pf1 + "\"" + "," +
								"pf2:" + "\"" + pf2 + "\"" + "," +
	                            "pf3:" + "\"" + pf3 + "\"" + "});"
	        )
	        apply = graph.run(
	        	"match (s:student{name:\""+name+"\"}),(p:professor{name:\""+pf1+"\"}) \n" +
	        	"create (s)-[r:UnderProf]->(p) \n"+
	        	"return r, s, p "
	        	)
	        return HttpResponse("Your Application has been submitted")



def prof(request):
	return render (request, "professor.html", {})

@csrf_exempt
def profreg(request):
	if request.method=="GET":
		return render (request, "register.html", {})
	if request.method=="POST" :
	    try:
	        form = request.POST
	        name = form["name"]
	        research = form["research"]
	        email = form["email"]
	        password = form["password"]
	        vacancy = form["vacancy"]
	    except KeyError:
	        return JsonResponse({"respose": "Some error occurred"})
	    else:
	        results = graph.run(
	        "create (n:professor{name:" + "\"" + name + "\"" + "," + 
	                            "research:" + "\"" + research + "\"" + "," +
	                            "email:" + "\"" + email + "\"" + "," +
	                            "password:" + "\"" + password + "\"" + "," +
	                            "vacancy:" + "\"" + vacancy + "\"" + "});"
	        )
	        print(results)
	        return JsonResponse({"response": "Registered successfully"})

@csrf_exempt
def login(request):
	if request.method=="GET" :
		return render (request, "login.html", {})
	if request.method=="POST" :
	    try:
	        form = request.POST
	        email = form["email"]
	        password = form["password"]
	    except KeyError:
	        return JsonResponse({"respose": "Some error occurred"})
	    else:
	        selector = NodeSelector(graph)
	        results = selector.select("professor",email=email,password=password).first()
	        print(results)
	        if(results==None):
	            return JsonResponse({"response":"Incorrect username or password"})
	        else:
	            obj = AES.new('This is a key123', AES.MODE_CFB, 'This is an IV456')
	            message = results['password']
	            ciphertext = obj.encrypt(message)

	            #obj2 = AES.new('This is a key123', AES.MODE_CFB, 'This is an IV456')
	            #obj2.decrypt(ciphertext)
#	            try :
                res = graph.run(
                    "match (s:student)-[r:UnderProf]->(p:professor) where (p.email=\""+form["email"]+"\") return s.name"
                    ).data()
                print (res)
                cont = {}
                cont["applied"] = [str(row["s.name"]).replace("{","").replace("}","") for row in res ]
                print (cont)
                cont["profmail"] = form["email"]
                return render (request, "profhome.html", cont)
#	            except :
#	                return render (request, "profhome.html", {})

#	            return JsonResponse({"response":"Login Success",
#	                    "name": results['name'],
#	                    "email": results['email'],
#	                    "research": results['research'],
#	                    "vacancy": results['vacancy'],
#	                    "api-token": ciphertext.decode('ISO-8859-1')})

	return render (request, "login.html", {})


@csrf_exempt
def select(request):
	if request.method=="POST":
		form = request.POST
		print (form)

		for key, value in form.items():
			if value == "yes" :
				apply = graph.run(
		        	#"match (s:student{name:\""+key+"\"}),(p:professor{name:\""+form["professor"]+"\"}) \n" +
		        	"match (s:student)-[r:UnderProf]->(p:professor) where s.name=\""+key+"\" and p.email = \""+form["profmail"]+"\" \n"+
		        	"delete r"
		        	).data()
				print (apply)
				intern = graph.run(
	        	"match (s:student{name:\""+key+"\"}),(p:professor{email:\""+form["profmail"]+"\"}) \n" +
	        	"create (s)-[r:hired]->(p) \n"+
	        	"return r, s, p "
	        	).data()
				print (intern)

			if value == "no" :
				apply = graph.run(
		        	#"match (s:student{name:\""+key+"\"}),(p:professor{name:\""+form["professor"]+"\"}) \n" +
		        	"match (s:student)-[r:UnderProf]->(p:professor) where s.name=\""+key+"\" and p.email = \""+form["profmail"]+"\" \n"+
		        	"delete r \n" +
		        	"return s.pf1, s.pf2, s.pf3, p.name "
		        	).data()

				print (apply)

				if apply[0]["s.pf1"] == apply[0]["p.name"] :
					next = graph.run(
		        	"match (s:student{name:\""+key+"\"}),(p:professor{name:\""+apply[0]["s.pf2"]+"\"}) \n" +
		        	"create (s)-[r:UnderProf]->(p) \n"+
		        	"return r, s, p "
		        	)
				if apply[0]["s.pf2"] == apply[0]["p.name"] :
					next = graph.run(
		        	"match (s:student{name:\""+key+"\"}),(p:professor{name:\""+apply[0]["s.pf3"]+"\"}) \n" +
		        	"create (s)-[r:UnderProf]->(p) \n"+
		        	"return r, s, p "
		        	)
		return JsonResponse ({"status":"Done"})
