from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Project, ProjectFeature
from grants.models import GrantPreferences


class ProjectSetupForm(forms.ModelForm):
    """Core project setup form"""
    
    class Meta:
        model = Project
        fields = [
            'name', 'type', 'genre', 'logline', 'budget_range',
            'synopsis', 'estimated_budget', 'currency', 'project_stage'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter project name'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'logline': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Brief one-line description'}),
            'synopsis': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5, 'placeholder': 'Detailed project synopsis'}),
            'budget_range': forms.Select(attrs={'class': 'form-select'}),
            'estimated_budget': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'project_stage': forms.Select(attrs={'class': 'form-select'}),
        }


class ProjectCoreDataForm(forms.ModelForm):
    """Extended core project data for grant features"""
    
    # Multiple choice fields
    genres_list = forms.MultipleChoiceField(
        choices=[
            ('action', 'Action'), ('adventure', 'Adventure'), ('comedy', 'Comedy'),
            ('drama', 'Drama'), ('horror', 'Horror'), ('romance', 'Romance'),
            ('thriller', 'Thriller'), ('sci_fi', 'Science Fiction'), ('fantasy', 'Fantasy'),
            ('documentary', 'Documentary'), ('animation', 'Animation'), ('experimental', 'Experimental'),
            ('family', 'Family'), ('musical', 'Musical'), ('western', 'Western')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False
    )
    
    themes_list = forms.MultipleChoiceField(
        choices=[
            ('social_justice', 'Social Justice'), ('environmental', 'Environmental'),
            ('diversity', 'Diversity & Inclusion'), ('mental_health', 'Mental Health'),
            ('education', 'Education'), ('community', 'Community Stories'),
            ('historical', 'Historical'), ('cultural', 'Cultural Heritage'),
            ('youth', 'Youth Focused'), ('seniors', 'Senior Stories'),
            ('disability', 'Disability Awareness'), ('immigration', 'Immigration'),
            ('gender_equality', 'Gender Equality'), ('poverty', 'Poverty & Economic Justice')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False
    )
    
    languages_list = forms.MultipleChoiceField(
        choices=[
            ('english', 'English'), ('spanish', 'Spanish'), ('french', 'French'),
            ('mandarin', 'Mandarin'), ('hindi', 'Hindi'), ('arabic', 'Arabic'),
            ('portuguese', 'Portuguese'), ('russian', 'Russian'), ('japanese', 'Japanese'),
            ('german', 'German'), ('italian', 'Italian'), ('korean', 'Korean'),
            ('other', 'Other')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False
    )
    
    diversity_flags_list = forms.MultipleChoiceField(
        choices=[
            ('female_director', 'Female Director'), ('poc_director', 'POC Director'),
            ('lgbtq_director', 'LGBTQ+ Director'), ('disabled_director', 'Director with Disability'),
            ('emerging_director', 'Emerging Director'), ('female_producer', 'Female Producer'),
            ('poc_producer', 'POC Producer'), ('diverse_cast', 'Diverse Cast'),
            ('diverse_crew', 'Diverse Crew'), ('indigenous', 'Indigenous Stories'),
            ('veteran', 'Veteran Stories'), ('student_film', 'Student Film')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False
    )
    
    # Location fields
    production_country = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'United States'}),
        required=False
    )
    production_state = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'California'}),
        required=False
    )
    production_city = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Los Angeles'}),
        required=False
    )
    
    class Meta:
        model = Project
        fields = []  # We'll handle this manually in save()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Populate from existing data
            self.fields['genres_list'].initial = self.instance.genres
            self.fields['themes_list'].initial = self.instance.themes
            self.fields['languages_list'].initial = self.instance.languages
            self.fields['diversity_flags_list'].initial = self.instance.diversity_flags
            
            location = self.instance.production_location
            if location:
                self.fields['production_country'].initial = location.get('country', '')
                self.fields['production_state'].initial = location.get('state', '')
                self.fields['production_city'].initial = location.get('city', '')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Update JSON fields
        instance.genres = self.cleaned_data.get('genres_list', [])
        instance.themes = self.cleaned_data.get('themes_list', [])
        instance.languages = self.cleaned_data.get('languages_list', [])
        instance.diversity_flags = self.cleaned_data.get('diversity_flags_list', [])
        
        # Update location
        instance.production_location = {
            'country': self.cleaned_data.get('production_country', ''),
            'state': self.cleaned_data.get('production_state', ''),
            'city': self.cleaned_data.get('production_city', '')
        }
        
        if commit:
            instance.save()
        return instance


class GrantPreferencesForm(forms.ModelForm):
    """Grant-specific preferences and setup form (15 fields)"""
    
    preferred_funding_types = forms.MultipleChoiceField(
        choices=[
            ('grant', 'Grant'), ('tax_credit', 'Tax Credit'), ('rebate', 'Rebate'),
            ('loan', 'Loan'), ('equity', 'Equity'), ('mixed', 'Mixed')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False,
        label="Preferred Funding Types"
    )
    
    funding_priorities = forms.MultipleChoiceField(
        choices=GrantPreferences.FUNDING_PRIORITIES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False,
        label="Funding Priorities"
    )
    
    preferred_regions = forms.MultipleChoiceField(
        choices=[
            ('north_america', 'North America'), ('europe', 'Europe'), ('asia', 'Asia'),
            ('australia', 'Australia/Oceania'), ('africa', 'Africa'), ('south_america', 'South America'),
            ('local', 'Local/Regional'), ('national', 'National'), ('international', 'International')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False,
        label="Preferred Regions"
    )
    
    excluded_regions = forms.MultipleChoiceField(
        choices=[
            ('none', 'No Exclusions'),
            ('requires_residency', 'Requires Local Residency'),
            ('non_english', 'Non-English Speaking Regions'),
            ('complex_tax', 'Complex Tax Jurisdictions')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False,
        label="Excluded Regions"
    )
    
    max_application_complexity = forms.ChoiceField(
        choices=[
            (1, '1 - Simple (Basic application form)'),
            (2, '2 - Easy (Form + 1-2 documents)'),
            (3, '3 - Moderate (Form + multiple documents)'),
            (4, '4 - Complex (Detailed application + references)'),
            (5, '5 - Very Complex (Extensive requirements)')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial=3,
        label="Maximum Application Complexity"
    )
    
    lead_time_preference = forms.IntegerField(
        validators=[MinValueValidator(7), MaxValueValidator(365)],
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '30'}),
        initial=30,
        label="Minimum Lead Time (days before deadline)",
        help_text="How many days notice do you need before a grant deadline?"
    )
    
    genre_requirements = forms.MultipleChoiceField(
        choices=[
            ('any', 'Any Genre'),
            ('documentary_only', 'Documentary Only'),
            ('narrative_only', 'Narrative Only'),
            ('experimental', 'Experimental/Art'),
            ('educational', 'Educational Content'),
            ('commercial', 'Commercial Projects')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False,
        label="Genre Requirements"
    )
    
    theme_requirements = forms.MultipleChoiceField(
        choices=[
            ('any', 'Any Theme'),
            ('social_impact', 'Social Impact Required'),
            ('diversity_focused', 'Diversity Focused'),
            ('environmental', 'Environmental Themes'),
            ('educational', 'Educational Value'),
            ('community_based', 'Community Based')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False,
        label="Theme Requirements"
    )
    
    diversity_requirements = forms.MultipleChoiceField(
        choices=[
            ('none', 'No Specific Requirements'),
            ('female_director', 'Female Director'),
            ('poc_director', 'POC Director'),
            ('emerging_filmmaker', 'Emerging Filmmaker'),
            ('diverse_cast_crew', 'Diverse Cast/Crew'),
            ('underrepresented_stories', 'Underrepresented Stories')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False,
        label="Diversity Requirements"
    )
    
    company_age_minimum = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0'}),
        required=False,
        label="Company Age Minimum (years)",
        help_text="Minimum years your company has been in business"
    )
    
    auto_apply_threshold = forms.IntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '80'}),
        initial=80,
        label="Auto-Apply Match Threshold (%)",
        help_text="Match score threshold for automatic application consideration"
    )
    
    class Meta:
        model = GrantPreferences
        fields = [
            'min_amount', 'max_amount', 'recurring_grants_only', 
            'track_record_required', 'collaboration_required',
            'auto_apply_enabled'
        ]
        widgets = {
            'min_amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '1000.00'}),
            'max_amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '100000.00'}),
            'recurring_grants_only': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'track_record_required': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'collaboration_required': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'auto_apply_enabled': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'min_amount': 'Minimum Grant Amount',
            'max_amount': 'Maximum Grant Amount',
            'recurring_grants_only': 'Recurring Grants Only',
            'track_record_required': 'Track Record Required',
            'collaboration_required': 'Collaboration Required',
            'auto_apply_enabled': 'Enable Auto-Application',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Populate choice fields from JSON data
            self.fields['preferred_funding_types'].initial = self.instance.preferred_funding_types
            self.fields['funding_priorities'].initial = self.instance.funding_priorities
            self.fields['preferred_regions'].initial = self.instance.preferred_regions
            self.fields['excluded_regions'].initial = self.instance.excluded_regions
            self.fields['genre_requirements'].initial = self.instance.genre_requirements
            self.fields['theme_requirements'].initial = self.instance.theme_requirements
            self.fields['diversity_requirements'].initial = self.instance.diversity_requirements
            self.fields['max_application_complexity'].initial = self.instance.max_application_complexity
            self.fields['lead_time_preference'].initial = self.instance.lead_time_preference
            self.fields['auto_apply_threshold'].initial = self.instance.auto_apply_threshold
            self.fields['company_age_minimum'].initial = self.instance.company_age_minimum
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Update JSON fields
        instance.preferred_funding_types = self.cleaned_data.get('preferred_funding_types', [])
        instance.funding_priorities = self.cleaned_data.get('funding_priorities', [])
        instance.preferred_regions = self.cleaned_data.get('preferred_regions', [])
        instance.excluded_regions = self.cleaned_data.get('excluded_regions', [])
        instance.genre_requirements = self.cleaned_data.get('genre_requirements', [])
        instance.theme_requirements = self.cleaned_data.get('theme_requirements', [])
        instance.diversity_requirements = self.cleaned_data.get('diversity_requirements', [])
        instance.max_application_complexity = int(self.cleaned_data.get('max_application_complexity', 3))
        instance.lead_time_preference = self.cleaned_data.get('lead_time_preference', 30)
        instance.auto_apply_threshold = self.cleaned_data.get('auto_apply_threshold', 80)
        instance.company_age_minimum = self.cleaned_data.get('company_age_minimum')
        
        if commit:
            instance.save()
        return instance


class ProjectFeatureSetupForm(forms.Form):
    """Form for enabling project features"""
    
    FEATURE_CHOICES = [
        ('grants', 'Grant Discovery & Tracking'),
        ('budget', 'Budget Builder'),
        ('schedule', 'Production Schedule'),
        ('festivals', 'Festival Research & Submissions'),
        ('script', 'Script Analysis & Breakdown'),
    ]
    
    features = forms.MultipleChoiceField(
        choices=FEATURE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox feature-checkbox'}),
        required=False,
        label="Enable Features"
    )
    
    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.fields['features'].initial = project.features_enabled