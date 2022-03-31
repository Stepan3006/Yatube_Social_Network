from django import forms

from .models import Comment, Group, Post


class PostForm(forms.ModelForm):
    text = forms.CharField(
        label='Текст публикации',
        widget=forms.Textarea,
    )
    group = forms.ModelChoiceField(
        label='Название группы',
        queryset=Group.objects.all(),
        required=False,
    )

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Поле обязательное для заполнения!')
        return(data)


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        label='Текст комментария',
        widget=forms.Textarea,
    )

    class Meta:
        model = Comment
        fields = ['text']

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Поле обязательное для заполнения!')
        return(data)
