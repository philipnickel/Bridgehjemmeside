# Forms API Reference

Django forms handle user input validation and rendering. This page documents all form classes.

## Form Classes

::: club_management.forms
    options:
        show_source: true
        heading_level: 2
        members_order: source

## Form Usage

Forms in Django handle both rendering HTML and validating submitted data:

!!! example "Basic form usage in views"
    
    ```python
    from django.shortcuts import render, redirect
    from .forms import SomeForm
    
    def form_view(request):
        if request.method == 'POST':
            form = SomeForm(request.POST)
            if form.is_valid():
                # Process valid form data
                form.save()
                return redirect('success_url')
        else:
            form = SomeForm()
        
        return render(request, 'template.html', {'form': form})
    ```

!!! example "Form rendering in templates"
    
    ```html
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Submit</button>
    </form>
    ```

## Form Validation

Django forms provide both field-level and form-level validation:

- **Field validation**: Handled by field types (CharField, EmailField, etc.)
- **Custom validation**: Override `clean_<fieldname>()` methods
- **Form-level validation**: Override `clean()` method for cross-field validation