import os

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile, Competition, CompetitionResult, Registration, Kit, KitImage, Sponsor, \
    Feedback, GuideFile, Team
import re
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.utils import timezone
from PIL import Image as PILImage
from django.contrib.auth import get_user_model


class UserRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, label="Họ và tên", required=True)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy', 'class': 'form-control'}, format='%d/%m/%Y'),
        input_formats=['%d/%m/%Y'],
        label="Ngày sinh (dd/mm/yyyy)",
        required=True
    )
    address = forms.CharField(max_length=255, label="Địa chỉ", required=True)
    school_name = forms.CharField(max_length=255, label="Đang là học sinh trường", required=False)
    role = forms.ChoiceField(
        choices=[('student', 'Thí sinh'), ('coach', 'Huấn luyện viên')],
        widget=forms.RadioSelect,
        label="Vai trò",
        required=True
    )
    profile_picture = forms.ImageField(required=False, label="Ảnh đại diện")
    phone_number = forms.CharField(max_length=15, label="Số điện thoại", required=True)
    email = forms.EmailField(label="Email", required=True)

    # Điều chỉnh trường gender để bỏ đi lựa chọn "khác" và bắt buộc
    gender = forms.ChoiceField(
        choices=[('nam', 'Nam'), ('nữ', 'Nữ')],
        widget=forms.RadioSelect,
        initial='nam',
        label="Giới tính",
        required=True
    )

    id_number = forms.CharField(max_length=20, label="Số CMND/CCCD", required=False)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'full_name', 'date_of_birth', 'address', 'school_name',
            'role', 'profile_picture', 'phone_number', 'email', 'gender',
            'id_number', 'password1', 'password2'
        ]

    # Các phương thức clean cho từng trường
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
        if CustomUser.objects.filter(phone_number=phone_number).exists():
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


class RegistrationForm(forms.ModelForm):
    # Thêm trường tùy chỉnh không thuộc về model
    agree_rules = forms.BooleanField(
        label="Tôi đồng ý với Thể lệ và các Quy định của Cuộc thi",
        required=True,
        error_messages={'required': 'Bạn phải đồng ý với Thể lệ để tiếp tục.'}
    )
    confirm_info = forms.BooleanField(
        label="Tôi đã kiểm tra kỹ thông tin thí sinh và chịu trách nhiệm",
        required=True,
        error_messages={'required': 'Bạn phải xác nhận thông tin đã cung cấp.'}
    )

    class Meta:
        model = Registration
        fields = [
            'region', 'city', 'competition_group', 'team_name', 'team_email',
            'coach_name', 'coach_unit', 'coach_phone',
            'guardian_name', 'relationship', 'guardian_phone', 'guardian_email',
            'student_name', 'student_phone', 'student_email', 'student_class',
            'birth_year', 'gender', 'ethnicity', 'address', 'student_photo', 'member_count'
        ]
        labels = {
            'region': 'Khu vực đăng ký',
            'city': 'Tỉnh/Thành phố',
            'competition_group': 'Bảng thi',
            'team_name': 'Tên đội thi',
            'team_email': 'Email đội thi',
            'coach_name': 'Họ tên HLV',
            'coach_unit': 'Đơn vị công tác',
            'coach_phone': 'Số điện thoại HLV',
            'member_count': 'Số lượng thí sinh',
            'guardian_name': 'Họ và tên phụ huynh',
            'relationship': 'Quan hệ với thí sinh',
            'guardian_phone': 'Số điện thoại phụ huynh',
            'guardian_email': 'Email phụ huynh',
            'student_name': 'Họ và tên thí sinh',
            'student_phone': 'Số điện thoại thí sinh',
            'student_email': 'Email thí sinh',
            'student_class': 'Lớp, trường',
            'birth_year': 'Năm sinh',
            'gender': 'Giới tính',
            'ethnicity': 'Dân tộc',
            'address': 'Địa chỉ thường trú',
            'student_photo': 'Ảnh chân dung thí sinh',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    # Xóa required=True cho các trường không bắt buộc
    student_phone = forms.CharField(required=False)  # Không bắt buộc
    student_email = forms.EmailField(required=False)  # Không bắt buộc

    def clean(self):
        cleaned_data = super().clean()
        agree_rules = cleaned_data.get("agree_rules")
        confirm_info = cleaned_data.get("confirm_info")

        if not agree_rules:
            raise ValidationError("Bạn phải đồng ý với Thể lệ và các Quy định của Cuộc thi.")

        if not confirm_info:
            raise ValidationError("Bạn phải xác nhận thông tin đã cung cấp.")

        return cleaned_data


class EditRegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = [
            'region', 'city', 'competition_group', 'team_name', 'team_email',
            'coach_name', 'coach_unit', 'coach_phone',
            'guardian_name', 'relationship', 'guardian_phone', 'guardian_email',
            'student_name', 'student_phone', 'student_email', 'student_class',
            'birth_year', 'gender', 'ethnicity', 'address', 'student_photo', 'member_count'
        ]
        labels = {
            'region': 'Khu vực đăng ký',
            'city': 'Tỉnh/Thành phố',
            'competition_group': 'Bảng thi',
            'team_name': 'Tên đội thi',
            'team_email': 'Email đội thi',
            'coach_name': 'Họ tên HLV',
            'coach_unit': 'Đơn vị công tác',
            'coach_phone': 'Số điện thoại HLV',
            'member_count': 'Số lượng thí sinh',
            'guardian_name': 'Họ và tên phụ huynh',
            'relationship': 'Quan hệ với thí sinh',
            'guardian_phone': 'Số điện thoại phụ huynh',
            'guardian_email': 'Email phụ huynh',
            'student_name': 'Họ và tên thí sinh',
            'student_phone': 'Số điện thoại thí sinh',
            'student_email': 'Email thí sinh',
            'student_class': 'Lớp, trường',
            'birth_year': 'Năm sinh',
            'gender': 'Giới tính',
            'ethnicity': 'Dân tộc',
            'address': 'Địa chỉ thường trú',
            'student_photo': 'Ảnh chân dung thí sinh',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    # Đảm bảo các trường không bắt buộc nếu cần
    student_phone = forms.CharField(required=False)
    student_email = forms.EmailField(required=False)

    def clean(self):
        # Có thể thêm các bước kiểm tra và xác thực cần thiết
        cleaned_data = super().clean()
        # Ví dụ: kiểm tra số lượng thí sinh hợp lệ
        member_count = cleaned_data.get("member_count")
        if member_count is not None and member_count <= 0:
            raise ValidationError("Số lượng thí sinh phải lớn hơn 0.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Làm cho các trường "competition_group" và "member_count" chỉ có thể đọc được
        self.fields['competition_group'].widget.attrs['readonly'] = True
        self.fields['member_count'].widget.attrs['readonly'] = True


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
        fields = ['full_name', 'date_of_birth', 'address', 'school_name',
                  'phone_number', 'profile_picture', 'gender']
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
        fields = ['bio', 'interests', 'social_links']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'interests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'social_links': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CompetitionForm(forms.ModelForm):
    new_image = forms.ImageField(required=False)  # Thêm trường new_image
    rounds = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Nhập thông tin vòng thi dưới dạng JSON'}),
        required=False
    )
    groups = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Nhập thông tin các bảng đấu dưới dạng JSON'}),
        required=False
    )

    class Meta:
        model = Competition
        fields = [
            'name', 'description', 'registration_start_date', 'registration_end_date',
            'rules', 'max_participants', 'image',
            'first_prize_points', 'second_prize_points',
            'third_prize_points', 'potential_points',
            'participants_target', 'location', 'rounds', 'groups'
        ]

        widgets = {
            'registration_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'registration_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def save(self, commit=True):
        competition = super().save(commit=False)

        # Đặt is_active dựa vào registration_end_date
        competition.is_active = competition.registration_end_date >= timezone.now().date()

        # Chuyển đổi chuỗi JSON thành danh sách và gán cho trường rounds và groups
        if self.cleaned_data['rounds']:
            competition.rounds = self.cleaned_data['rounds']
        if self.cleaned_data['groups']:
            competition.groups = self.cleaned_data['groups']

        if commit:
            competition.save()
        return competition


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


class GuideFileForm(forms.ModelForm):
    class Meta:
        model = GuideFile
        fields = ['file', 'note', 'document_name']


User = get_user_model()


class UserRoleForm(forms.Form):
    ROLE_CHOICES = [
        ('student', 'Học sinh thi đấu'),
        ('coach', 'Huấn luyện viên'),
        ('admin', 'Admin'),
        ('leader', 'Trưởng Ban Tổ Chức'),
        ('deputy_leader', 'Phó Ban Tổ Chức'),
        ('referee', 'Trưởng Ban Trọng Tài'),
    ]
    username = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Tên đăng nhập'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Chọn vai trò")


