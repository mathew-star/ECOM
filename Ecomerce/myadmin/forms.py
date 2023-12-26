
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django import forms
from django.forms import inlineformset_factory
from myadmin.models import MyProducts,ProductImages,Variant, Size, Color
from .models import CustomUser
from django.forms import inlineformset_factory
from django.apps import apps
Category = apps.get_model('myadmin', 'Category')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_listed']
        
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_listed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def clean_name(self):
       name = self.cleaned_data.get('name')
       if not name:
           raise ValidationError('Name is required')
       return name

    def clean_description(self):
       description = self.cleaned_data.get('description')
       if not description:
           raise ValidationError('Description is required')
       return description

    def clean_image(self):
       image = self.cleaned_data.get('image')
       if not image:
           raise ValidationError('Image is required')
       else:
           file_extension = image.name.split('.')[-1].lower()
           if file_extension not in ['jpg', 'jpeg', 'png', 'gif']:
               raise ValidationError('Invalid image file')
       return image

    def clean_is_listed(self):
       is_listed = self.cleaned_data.get('is_listed')
       if is_listed is None:
           raise ValidationError('Must choose a category')
       return is_listed
    

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Products
#         fields = ['name', 'description', 'category', 'price', 'is_listed', 'rating', 'star']

#     def clean_name(self):
#         name = self.cleaned_data.get('name')
#         if len(name)<3:
#             raise forms.ValidationError('Name must be at least 3 characters long.')
#         return name

#     def clean_description(self):
#         description = self.cleaned_data.get('description')
#         if len(description) < 10:
#             raise forms.ValidationError('Description must be at least 10 characters long.')
#         return description

#     def clean_price(self):
#         price = self.cleaned_data.get('price')
#         if price <= 0:
#             raise forms.ValidationError('Price must be greater than zero.')
#         return price

# ProductImageFormSet = inlineformset_factory(Products, ProductImages, fields=['image'], extra=1)


class ProductForm(forms.ModelForm):

    class Meta:
        model = MyProducts  # Corrected the model name
        fields = ['name', 'description', 'category', 'is_listed']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'})
        }

class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name']

class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        fields = ['size', 'quantity', 'price']
        widgets = {
            'size': forms.Select(attrs={'class': 'form-control'})
        }
    size = forms.ModelChoiceField(queryset=Size.objects.all())

class ImageForm(forms.ModelForm):
    class Meta:
        model = ProductImages
        fields = ['image']

VariantFormSet = inlineformset_factory(
    MyProducts, 
    Variant, 
    form=VariantForm, 
    fields=['size', 'quantity', 'price'],
    extra=1, 
    can_delete=True
)

ImageFormSet = inlineformset_factory(
    MyProducts, 
    ProductImages, 
    form=ImageForm, 
    fields=['image'],
    extra=1, 
    can_delete=True
)
