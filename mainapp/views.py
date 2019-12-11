from .models import Profile, Interaction, CredentialsModel
from django.contrib.auth.models import User
import httplib2
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth import logout
from googleapiclient.discovery import build
from snowflake import settings
from oauth2client.contrib import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.contrib.django_util.storage import DjangoORMStorage
from django.shortcuts import render
from httplib2 import Http
import requests
from newsapi import NewsApiClient
import json
from random import shuffle
from enum import Enum

def homepage(request):
    status = True
    if not request.user.is_authenticated:
        return render(request=request, template_name="mainapp/homepage.html")

    storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    
    try:
        access_token = credential.access_token
        resp, cont = Http().request("https://www.googleapis.com/auth/gmail.readonly",headers={'Host': 'www.googleapis.com','Authorization': access_token})
 
    except:
        status = False
        print('gmail access failed')
        
    return render(request=request, template_name="mainapp/homepage.html")

FLOW = flow_from_clientsecrets(
    settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
    scope='https://www.googleapis.com/auth/gmail.readonly',
    redirect_uri='http://127.0.0.1:8000/oauth2callback',
    prompt='consent')


def gmail_authenticate(request):
    storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build('gmail', 'v1', http=http)
        print('GMAIL_AUTHENTICATE PARTIAL EXECUTION')
        print('access_token = ', credential.access_token)
        status = True
        access_token = credential.access_token
        
        dbMessageslist = []
        messageslist = []
        contacts = []
        
        messages = service.users().messages().list(userId='me',maxResults=10).execute().get('messages', [])
        
        for message in messages:
            print('\n\n********new*******')
            
            dbData = {}
            data = {}
            mdata = service.users().messages().get(userId='me', id=message['id']).execute()
            print(mdata)
            class label(Enum):
                recieved = 1
                sent = 2
                draft = 3
            
            data['id'] = mdata['id']
            
            data['snippet'] = (mdata['snippet']).replace('&#39;',"'")
            
            data['label'] = label.recieved.name
            if 'SENT' in mdata['labelIds']:
                data['label'] = label.sent.name            
            if 'DRAFT' in mdata['labelIds']:
                data['label'] = label.draft.name
            
            for smalldicts in mdata['payload']['headers']:
                if smalldicts['name'] == 'From':
                    data['from'] = ( ((smalldicts['value']).split('<'))[0] ).strip()
                    data['sender_email'] = ( ((smalldicts['value']).split('<'))[1] ).strip()
                    if ' ' in data['from']:
                        contact = ((( (data['sender_email']).split('@') )[1]).split('.'))[0]

                        if contact not in contacts:
                            contacts.append(contact.lower())
                
                if smalldicts['name'] == 'To':
                    data['to'] = ((smalldicts['value']).split('<'))[0]

                if smalldicts['name'] == 'Subject':
                    data['subject'] = smalldicts['value']

                if smalldicts['name'] == 'Date':
                    data['date'] = smalldicts['value']

                
            #bools = {'html' : 'False', 'text' : 'True'}

            try:
                #print(data)
                data['html'] = mdata['payload']['parts'][1]['body']['data']
                #bools['html'] = True
                data['text'] = mdata['payload']['parts'][0]['body']['data']
                #bools['text'] = True
            except:
                print("WHERE ERROR OCCURED")
            
            if data['label'] == label.recieved:
                dbData['contact'] = data['from']
            
            else:
                dbData['contact'] = data['to']

            
            dbData['subject'] = data['subject']
            dbData['label'] = data['label']
            dbData['date'] = data['date']
            dbMessageslist.append(dbData)
            messageslist.append(data)
            #print(dbData)

            entry, created = Interaction.objects.get_or_create(messageId=data['id'])
            entry.user = request.user
            entry.sender = data['from']
            entry.sender_email = data['sender_email']
            entry.reciever = data['to']
            entry.date = data['date']
            entry.subject = data['subject']
            entry.label = data['label']
            entry.save()

        
        mailswant = True

        Profile.objects.filter(user=request.user).update(messages = str(dbMessageslist), contacts =str(contacts), token = access_token)
        #Interaction.objects.filter(user=request.user).update(reciever = data['to'], sender = data['from'], date = data['date'],subject = data['subject'], label = data['label'])
        
        return render(request, 'mainapp/homepage.html', {'status': status, 'access_token': access_token,'messageslist' : messageslist, 'mailswant': mailswant})


def auth_return(request):
    get_state = bytes(request.GET.get('state'), 'utf8')
    if not xsrfutil.validate_token(settings.SECRET_KEY, get_state,
                                   request.user):
        return HttpResponseBadRequest()
    credential = FLOW.step2_exchange(request.GET.get('code'))
    storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
    storage.put(credential)
    print("access_token: %s" % credential.access_token)
    print('AUTH_RETURN GOT EXECUTED')
    return HttpResponseRedirect("/")

def Logout(request):
	logout(request)
	return render(request=request,template_name="mainapp/homepage.html")

def messages(request):
	print('HEREHERE')
	Profile.objects.filter(user=request.user).update(messages = '')
	return render(request=request,template_name="mainapp/homepage.html")

def dashboard(request):
    storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build('gmail', 'v1', http=http)
        print('GMAIL_AUTHENTICATE PARTIAL EXECUTION')
        print('access_token = ', credential.access_token)
        status = True
        access_token = credential.access_token
        senders = []
        messages = service.users().messages().list(userId='me',maxResults=10).execute().get('messages', [])
        for message in messages:
            mdata = service.users().messages().get(userId='me', id=message['id']).execute()
            for smalldicts in mdata['payload']['headers']:
                if smalldicts['name'] == 'From':
                    sender = ( ((smalldicts['value']).split('<'))[0] ).strip()
                    senders.append(sender)
        
        queries = []
        for sender in senders:
            if sender not in queries:
                queries.append(sender)
        print(queries)
        
        articleslist = []
        newsapi = NewsApiClient(api_key='513c2df2888d486aa67cd3835954f80d')

        for query in queries:
            all_articles = newsapi.get_everything(q=query,
                                      from_param='2019-10-04',
                                      to='2019-10-05',
                                      language='en',
                                      sort_by='relevancy',)
            #print(all_articles)
            if (all_articles['totalResults'] > 0):
                for newsarticle in all_articles['articles']:
                    article = {}
                    article['query'] = query
                    article['source'] = newsarticle['source']['name']
                    article['title'] = newsarticle['title']
                    article['author'] = newsarticle['author']
                    article['content'] = newsarticle['content']
                    article['description'] = newsarticle['description']
                    article['url'] = newsarticle['url']
                    article['imgurl'] = newsarticle['urlToImage']
                    article['date'] = ( (newsarticle['publishedAt']).split('T') )[0]
                    articleslist.append(article)
                #print(articleslist, end='\n\n')
        dashboardwant = True
        shuffle(articleslist)
        return render(request, 'mainapp/homepage.html', {'status': status, 
                                                         'dashboardwant': dashboardwant,
                                                         'access_token': access_token,
                                                         'articleslist' : articleslist,})

