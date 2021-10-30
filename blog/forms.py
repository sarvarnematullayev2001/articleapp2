from django import forms
from .models import Post, Comment
from django.contrib.auth.models import User

class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'image', 'body', 'publish', 'status', 'tags')

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

class SearchForm(forms.Form):
    query = forms.CharField()