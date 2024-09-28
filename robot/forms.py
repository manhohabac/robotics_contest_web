import os

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile, Competition, CompetitionResult, Registration, Kit, KitImage, Sponsor, \
    Feedback
import re
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.utils import timezone
from PIL import Image as PILImage


class UserRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, label="Họ và tên")
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy', 'class': 'form-control'}, format='%d/%m/%Y'),
        input_formats=['%d/%m/%Y'],
        label="Ngày sinh (dd/mm/yyyy)"
    )
    address = forms.CharField(max_length=255, label="Địa chỉ")
    school_name = forms.CharField(max_length=255, label="Đang là học sinh trường")

    has_robot_competition_experience = forms.ChoiceField(
        choices=[(True, 'Đã từng'), (False, 'Chưa từng')],
        widget=forms.RadioSelect,
        label="Đã từng tham gia các cuộc thi về robot"
    )
    profile_picture = forms.ImageField(required=False, label="Ảnh đại diện")
    phone_number = forms.CharField(max_length=15, required=False, label="Số điện thoại")
    email = forms.EmailField(label="Email")

    # Thêm các trường mới
    gender = forms.ChoiceField(
        choices=[('nam', 'Nam'), ('nữ', 'Nữ'), ('khác', 'Khác')],
        widget=forms.RadioSelect,
        initial='khác',
        label="Giới tính"
    )
    id_number = forms.CharField(max_length=20, required=False, label="Số CMND/CCCD")

    class Meta:
        model = CustomUser
        fields = [
            'username', 'full_name', 'date_of_birth', 'address', 'school_name',
            'has_robot_competition_experience', 'profile_picture', 'phone_number',
            'email', 'gender', 'id_number', 'password1', 'password2'
        ]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError("Username chỉ được chứa chữ cái, chữ số, và dấu gạch dưới.")
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Username đã tồn tại.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("Số điện thoại này đã được sử dụng.")
        return phone_number

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if id_number and CustomUser.objects.filter(id_number=id_number).exists():
            raise forms.ValidationError("Số CMND/CCCD này đã được sử dụng.")
        return id_number

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        if not re.search(r'[A-Z]', password1):
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất một chữ cái viết hoa.")
        if not re.search(r'[a-z]', password1):
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất một chữ cái viết thường.")
        if not re.search(r'[0-9]', password1):
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất một chữ số.")
        if not re.search(r'[@#$]', password1):
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất một ký tự đặc biệt (@, #, hoặc $).")
        return password1


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Mật khẩu cũ')
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Mật khẩu mới')
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                           label='Xác nhận mật khẩu mới')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get("current_password")
        if self.user and not self.user.check_password(current_password):
            raise ValidationError('Mật khẩu cũ không đúng.')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        if new_password and confirm_new_password and new_password != confirm_new_password:
            self.add_error('confirm_new_password', 'Mật khẩu mới không khớp.')

        if new_password:
            try:
                password_validation.validate_password(new_password, self.user)
            except ValidationError as e:
                self.add_error('new_password', e)


class EditProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'dd/mm/yyyy',
                'data-date-format': 'd/m/Y',  # Flatpickr date format
            },
            format='%d/%m/%Y'  # Ensure the widget formats the initial value
        ),
        input_formats=['%d/%m/%Y'],
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['full_name', 'date_of_birth', 'address', 'school_name', 'phone_number', 'profile_picture', 'gender']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'school_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'interests', 'social_links', 'is_competitor']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'interests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'social_links': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_competitor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super(EditUserProfileForm, self).__init__(*args, **kwargs)
        # Đặt checkbox được tick dựa vào giá trị hiện tại của instance
        if self.instance.is_competitor:
            self.fields['is_competitor'].initial = True


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['name', 'description', 'start_date', 'end_date',
                  'registration_deadline', 'rules', 'max_participants', 'image']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'registration_deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        competition = super().save(commit=False)
        # So sánh end_date với thời điểm hiện tại để đặt is_active
        if competition.end_date >= timezone.now().date():
            competition.is_active = True
        else:
            competition.is_active = False

        if commit:
            competition.save()
        return competition

    # Thêm trường upload ảnh mới
    new_image = forms.ImageField(required=False, label='Change')


class CompetitionResultForm(forms.ModelForm):
    class Meta:
        model = CompetitionResult
        fields = ['registration', 'score']
        widgets = {
            'registration': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        competition = kwargs.pop('competition', None)  # Nhận tham số competition
        super().__init__(*args, **kwargs)

        if competition:
            # Lọc các registration theo cuộc thi và is_cancelled=False
            registrations = Registration.objects.filter(
                competition=competition,
                is_cancelled=False
            )

            # Tạo danh sách lựa chọn cho registration với thông tin hiển thị mong muốn
            self.fields['registration'].queryset = registrations
            self.fields['registration'].choices = [
                (reg.id, f"{reg.user.full_name} - {reg.user.date_of_birth:%d-%m-%Y} - {reg.user.school_name}")
                for reg in registrations
            ]


class KitForm(forms.ModelForm):
    class Meta:
        model = Kit
        fields = ['name', 'description', 'image', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên bộ kit'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Nhập mô tả'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập giá bán', 'id': 'priceInput'}),  # Dùng TextInput thay vì NumberInput
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')  # Lấy giá trị từ trường price

        if price is None or price == '':
            return 0  # Trả về giá trị mặc định nếu không nhập gì

        # Đảm bảo giá trị luôn là chuỗi để có thể xử lý replace
        if isinstance(price, int):
            return price  # Nếu là số nguyên, trả về luôn

        # Nếu là chuỗi, loại bỏ dấu chấm hoặc dấu phẩy và chuyển thành số nguyên
        price = str(price).replace(',', '').replace('.', '')

        return int(price)


class KitImageForm(forms.ModelForm):
    class Meta:
        model = KitImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(),
        }


class SponsorForm(forms.ModelForm):
    class Meta:
        model = Sponsor
        fields = ['name', 'description', 'logo', 'website']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tên nhà tài trợ'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Mô tả về nhà tài trợ'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Liên kết website'
            }),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'content', 'rating', 'image']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Lấy định dạng file
            valid_extensions = ['jpg', 'jpeg', 'png']
            ext = os.path.splitext(image.name)[1][1:].lower()  # Lấy phần mở rộng và chuyển về chữ thường
            if ext not in valid_extensions:
                raise ValidationError('Định dạng file không hợp lệ. Chỉ cho phép các định dạng: jpg, jpeg, png.')

            # Kiểm tra định dạng thực sự của file
            try:
                img = PILImage.open(image)
                img.verify()  # Xác thực file có phải là một hình ảnh hay không
            except (IOError, SyntaxError) as e:
                raise ValidationError('File không phải là hình ảnh hợp lệ.')

        return image


