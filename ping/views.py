from urllib import response
from django.shortcuts import render
from django.http import HttpResponse
import sqlite3
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import isbnlib 
import uuid
import requests
from datetime import date, timedelta

def index(response):

    return render(response, 'ping/base.html')

def home(response):
    return render(response, 'ping/home.html', {})

@csrf_exempt
def livre(request):
    con = sqlite3.connect("bibliotheque.db", )

    livre_liste=[]
    id = str(uuid.uuid4())[:8]

    data = request.POST
    isbn_data = data.get("isbn", "")

    cover_isbnlib = isbnlib.cover(isbn_data)

    cover_openlibrary="https://covers.openlibrary.org/b/isbn/{}-L.jpg".format(isbn_data)
    img_size = requests.get(cover_openlibrary).content

    if len(img_size) == 807:
        cover_img=cover_isbnlib.get('thumbnail')  # type: ignore
    else:
        cover_img="https://covers.openlibrary.org/b/isbn/{}-L.jpg".format(isbn_data)

    book = isbnlib.meta(isbn_data)
    author_data = str(book.get('Authors'))[2:-2]
    title_data = str(book.get('Title'))
    publisher_data = str(book.get('Publisher'))
    
    if isbn_data == '':
        pass
    else:
        res_add_livre ='INSERT OR REPLACE INTO livre(mdp, isbn, titre, auteur, editeur, emprunt) VALUES ("'+id+'","'+isbn_data+'","'+title_data+'","'+author_data+'","'+publisher_data+'",0)'
        cur = con.cursor()
        cur.execute(res_add_livre)
        con.commit()

    cur = con.cursor()
    res__select_livre = cur.execute("SELECT * FROM livre")
    con.commit()

    for item in res__select_livre.fetchall():
        livre_liste.append(item)

    if data == {}:
        value_new_livre = ""
    else:
        value_new_livre = livre_liste[-1][1]

    con.commit()
    con.close()

    return render(request, 'ping/livre.html', {"livre": livre_liste, "item": value_new_livre, "cover": cover_img})

@csrf_exempt
def add(request):
    con = sqlite3.connect("bibliotheque.db")
    
    liste_adherent=[]
    id = str(uuid.uuid4())[:8]

    data = request.POST
    nom_data = data.get("nom", "")
    prenom_data = data.get("prenom", "")
    adresse_data = data.get("adresse", "")
    tel_data = data.get("tel", "")

    

    if nom_data == '' or prenom_data == "" or adresse_data == "" or tel_data == "":
        pass
    else:
        res_add_adherent ='INSERT OR REPLACE INTO adherent(nomAdherent, prenomAdherent, adresse, telephone, mdp) VALUES ("'+nom_data+'","'+prenom_data+'", "'+adresse_data+'","'+tel_data+'","'+id+'")'
        cur = con.cursor()
        cur.execute(res_add_adherent)
        con.commit()

    cur = con.cursor()
    res_select_adherent = cur.execute("SELECT * FROM adherent")
    con.commit()
  
    for item in res_select_adherent.fetchall():
        liste_adherent.append(item)

    if data == {}:
        value_new_adherent = ""
    else:
        value_new_adherent = liste_adherent[-1][1]

    return render(request, 'ping/add.html', {"item": value_new_adherent, "adherent_liste": liste_adherent})

@csrf_exempt
def delete(request):
    con = sqlite3.connect("bibliotheque.db")
    cur = con.cursor()

    book_delete=[]
    member_delete=[]

    data = request.POST
    id_data = data.get("id", "")
    isbn_data = data.get("book", "")

    res_delete_adherent="delete from adherent where mdp =:identifiant"
    res_delete_livre="delete from livre where mdp =:isbn"

    con_select_adherent = sqlite3.connect("bibliotheque.db")
    cur_select_adherent = con_select_adherent.cursor()
    res_select_adherent = cur_select_adherent.execute('SELECT * FROM adherent WHERE mdp="%s"' % id_data)
    retour2 = res_select_adherent.fetchall()

    con_select_adherent.commit()
    
    con_select_livre = sqlite3.connect("bibliotheque.db")
    cur_select_livre = con_select_livre.cursor()
    res_select_livre = cur_select_livre.execute('SELECT * FROM livre WHERE mdp="%s"' % isbn_data)
    con_select_livre.commit()
    retour = res_select_livre.fetchall()

    if data == {}:
        book_delete = ""
    else:
        if retour == []:
            book_delete = ""
        else:
            for item in retour:
                book_delete.append(item)

            book_delete = book_delete[0][1]

    if data == {}:
        member_delete = ""
    else:
        if retour2 == []:
            member_delete = ""
        else:
            for item in retour2:
                member_delete.append(item)

            member_delete = member_delete[0][1]

    cur.execute(res_delete_adherent,{"identifiant":id_data})
    cur.execute(res_delete_livre,{"isbn":isbn_data})

    con.commit()
    con.close()

    return render(request, 'ping/delete.html', {"item": member_delete, "item_book": book_delete})
    
@csrf_exempt
def emprunts(request):
    con = sqlite3.connect("bibliotheque.db", )
    con2 = sqlite3.connect("bibliotheque.db", )

    today_date = date.today()
    td = timedelta(-42)
    date_emprunt=str(today_date)
    date_retour=str(today_date+td)

    liste_emprunts = []
    livre_liste = []

    data = request.POST
    isbn_data = data.get("isbn", "")
    member_data = data.get("prenom", "")

    cur = con.cursor()
    # res_select_livre = cur.execute('SELECT * FROM livres WHERE isbn=?', [isbn_data] )
    
    cur2 = con2.cursor()
    res_select_livre = cur2.execute('SELECT * FROM livre WHERE isbn=?', [isbn_data] )
    con2.commit()

    for item in res_select_livre.fetchall():
        livre_liste.append(item)

    if data == {}:
        id_livre = ""
    else:
        id_livre = livre_liste[0][0]

    con2.commit()

    res_select_adherent = cur.execute('SELECT * FROM adherent WHERE mdp=?', [member_data] )
    
    con.commit()

    print(id_livre)

    book = isbnlib.meta(isbn_data)
    title_data = str(book.get('Title'))

    if isbn_data == '' and member_data == '':
        pass
    else:
        if res_select_livre.fetchall() == [] and res_select_adherent.fetchall() == []:
            pass
        else:
            res ='INSERT OR REPLACE INTO emprunt(isbn, identifiant, dateemprunt, dateretour) VALUES ("'+id_livre+'","'+member_data+'","'+date_emprunt+'","'+date_retour+'")'
            cur = con.cursor()
            cur.execute(res)
            
            con.commit()
            

    cur = con.cursor()
    res_select_emprunts = cur.execute("SELECT * FROM emprunt")
    con.commit()
    
    for item in res_select_emprunts.fetchall():
        liste_emprunts.append(item)

    if data == {}:
        value_new_emprunt = ""
        title_data = ""
    else:
        if res_select_livre.fetchall() == []:
            value_new_emprunt = ""
            title_data = ""
        else:
            value_new_emprunt = liste_emprunts[-1][1] + " / "

    cur.execute("UPDATE livre set emprunt = 1")

    con.commit()
    con.close()

    return render(request, 'ping/emprunts.html', {"item": value_new_emprunt, "liste_emprunts": liste_emprunts, "title": title_data})


@csrf_exempt
def retard(request):
    con = sqlite3.connect("bibliotheque.db")

    today_date = date.today()

    retour_loan=[]

    data = request.POST
    isbn_data = data.get("isbn", "")
    member_data = data.get("prenom", "")

    cur = con.cursor()
    cur.execute("delete from retour where isbn > 0")
    res = cur.execute('SELECT isbn, identifiant, dateretour FROM emprunt WHERE dateretour < ?', [today_date])
    test = res.fetchall()

    for i in range(len(test)):
        cur.execute('INSERT OR REPLACE INTO retour(isbn, identifiant, dateretard) VALUES("'+str(test[i][0]) +'","'+ str(test[i][1]) +'","'+ str(test[i][2])+'")')
    con.commit()

    book = isbnlib.meta(isbn_data)
    title_data = str(book.get('Title'))

    con_retour = sqlite3.connect("bibliotheque.db")
    cur_retour = con_retour.cursor()
    res_retour = cur_retour.execute('SELECT * FROM emprunt WHERE isbn="%s" AND identifiant="%s"' % (isbn_data,member_data))
    con_retour.commit()
    retour = res_retour.fetchall()

    book = isbnlib.meta(isbn_data)
    author_data = str(book.get('Authors'))[2:-2]
    title_data = str(book.get('Title'))
    publisher_data = str(book.get('Publisher'))
    
    if isbn_data == '':
        pass
    else:
        res_add_livre ='INSERT OR REPLACE INTO livre(mdp, isbn, titre, auteur, editeur) VALUES ("'+id+'","'+isbn_data+'","'+title_data+'","'+author_data+'","'+publisher_data+'")'
        cur = con.cursor()
        cur.execute(res_add_livre)
        con.commit()

    if data == {}:
        retour_loan = ""
        title_data = ""
    else:
        if retour == []:
            retour_loan = ""
            title_data = ""
        else:
            for item in retour:
                retour_loan.append(item)

            retour_loan = retour_loan[0][1] + " / "

    if isbn_data == '':
        pass
    else:
        con_retard = sqlite3.connect("bibliotheque.db")
        cur_retard = con_retard.cursor()

        cur_retard.execute('DELETE FROM emprunt WHERE isbn="%s" AND identifiant="%s"' % (isbn_data,member_data))
        cur_retard.execute('DELETE FROM retour WHERE isbn="%s" AND identifiant="%s"' % (isbn_data,member_data))
        con_retard.commit()

    

    res_retard = cur.execute("SELECT * FROM retour")
    con.commit()
    value_retard = res_retard.fetchall()

    con.close()

    return render(request, 'ping/retard.html', {"item_loan": retour_loan, "title": title_data, "delay": value_retard})