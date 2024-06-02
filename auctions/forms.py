from django import forms
from .models import Auction,Comment,Category

class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = ''
        self.fields['content'].widget.attrs.update({'class': 'form-control auction-coment'})

    class Meta:
        model = Comment
        fields = ['content']

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'price', 'photo', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'file-input'}),
            'category': forms.Select(
                choices=[(category.id, category.name) for category in Category.objects.all()],
                attrs={'class': 'form-control'}
            )
        }