from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Chat,Results,Therapy
from .forms import SignUpForm, EditProfileForm

# Create your views here.
@login_required(login_url='login')
def home(request):
    return render(request, 'home.html',{})


#user login function

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ('You have been Logged In!'))
            return redirect('home')
        else:
            messages.error(request, ('Error Logging In - Please check your details'))
            return redirect('login')
    else:
        return render(request, 'login.html',{})

#user logout function
def logout_user(request):
    logout(request)
    messages.success(request, ('You have been successfully Logout...'))
    return redirect('login')

#user register function
def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            login(request, user)
            messages.success(request, ('You have registered'))
            return redirect('home')
    else:
        form = SignUpForm()
    context = {'form':form}
    return render(request, 'register.html', context)

@login_required(login_url='login')
def diagnose(request):
    if request.method=="POST":
        
        qn1 = request.POST.get('1')
        qn2 = request.POST.get('2')
        qn3 = request.POST.get('3')
        qn4 = request.POST.get('4')
        qn5 = request.POST.get('5')
        qn6 = request.POST.get('6')
        qn7 = request.POST.get('7')

        total = int(qn1)+int(qn2)+int(qn3)+int(qn4)+int(qn5)+int(qn6)+int(qn7)
        min=70
        max=280
        finalscore =0

        finalscore=round(((total-min)/(max-min))*100)
        
        if finalscore>=0 and finalscore<33:
            tag="Minor"
        elif finalscore>33 and finalscore <66:
            tag = "Mild"
        elif finalscore>66 and finalscore<100:
            tag="Severe"
        check =Results.objects.filter(user=request.user).count()
        #finalscore = str(finalscore)
        if check>0:
            up = Results.objects.get(user=request.user)
            print(request.user)
            up.result=finalscore
            print(finalscore)
            up.tag =tag
            print(tag)
            up.created = timezone.now()
            up.save()
        else:
            b=Results(user=request.user,result=finalscore,tag=tag,created=timezone.now())
            b.save()

        return redirect('results')



    return render(request,'diagnose.html',{})
@login_required(login_url='login')
def results(request):
    obj = Results.objects.get(user=request.user)
    res = Therapy.objects.get(tag=obj.tag)

    return render(request,'results.html',{"therapy":res,"data":obj})
@login_required(login_url='login')
def map(request):

    return render(request, 'map.html',{})
@login_required(login_url='login')
def chat(request):
    import nltk
    from nltk.stem.lancaster import LancasterStemmer
    stemmer = LancasterStemmer()

    import numpy
    import tflearn
    import tensorflow
    import random
    import json
    import pickle


    with open("C:/Users/Nish/Project/Therapy/accounts/intents.json") as file:
        data=json.load(file)

    try:
	    with open("C:/Users/Nish/Project/Therapy/accounts/data.pickles", "rb") as f:
		    words,labels,training,output = pickle.load(f)

    except:
	    words=[]
	    labels=[]
	    docs_x=[]
	    docs_y=[]
	    for intent in data['intents']:
		    for pattern in intent['patterns']:
			    wrds=nltk.word_tokenize(pattern)
			    words.extend(wrds)
			    docs_x.append(wrds)
			    docs_y.append(intent["tag"])

		    if intent["tag"] not in labels:
			    labels.append(intent["tag"])

	    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
	    words = sorted(list(set(words)))

	    labels = sorted(labels)

	    training=[]
	    output =[]

	    out_empty = [0 for _ in range(len(labels))]
	    for x, doc in enumerate(docs_x):
		    bag=[]
		    wrds=[stemmer.stem(w) for w in doc]

		    for w in words:
			    if w in wrds:
				    bag.append(1)
			    else:
				    bag.append(0)

		    output_row=out_empty[:]
		    output_row[labels.index(docs_y[x])] = 1

		    training.append(bag)
		    output.append(output_row)

	    taining = numpy.array(training)
	    output=numpy.array(output)

	    with open("C:/Users/Nish/Project/Therapy/accounts/data.pickles", "wb") as f:
		    pickle.dump((words,labels,training,output), f)


    tensorflow.reset_default_graph()
    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
    net = tflearn.regression(net)
    model = tflearn.DNN(net)

    try:
	    model.load("C:/Users/Nish/Project/Therapy/accounts/model.tflearn")
    except:
	    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
	    model.save("C:/Users/Nish/Project/Therapy/accounts/model.tflearn")


    def bag_of_words(s,words):
	    bag=[0 for _ in range(len(words))]

	    s_words=nltk.word_tokenize(s)
	    s_words = [stemmer.stem(word.lower()) for word in s_words]
	    for se in s_words:
		    for i,w in enumerate(words):
			    if w==se:
				    bag[i]= 1
	    return numpy.array(bag)

    def chat():
        inp = request.POST.get('question')
        results = model.predict([bag_of_words(inp, words)])[0]
        result_index = numpy.argmax(results)
        tag = labels[result_index]
        if results[result_index]>0.7:
            for tg in data["intents"]:
                if tg["tag"] ==tag:
                    responses = tg["responses"]
            answer=(random.choice(responses))
        else:
            answer=("I have not be trained about that. Please ask another question")
        b = Chat(user=request.user,question=inp,response=answer,created=timezone.now())
        b.save()

    if request.method=="POST":
        chat()

    data = Chat.objects.filter(user=request.user)

    return render(request,'chat.html',{'data':data})
#user update profile
'''
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, ('You have Edited your profile...'))
            return redirect('home')
    else:
        form = EditProfileForm(instance=request.user)
    context = {'form':form}
    return render(request, 'authenticate/edit_profile.html', context)
'''
