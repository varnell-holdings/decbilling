Got it! Since you're using Python's built-in HTTP server with Jinja2, the polling approach will work best. Here's how to set it up:

## 1. Track when your page changes

First, you need to detect when the data changes. The simplest way is to check the modification time of your data source (file, database, etc.):

```python
import os

def get_last_modified():
    # Replace with your actual data file
    return os.path.getmtime('your_data_file.txt')
```

## 2. Add an endpoint to check for changes

Add this to your server code:

```python
@app.route('/check_updates')
def check_updates():
    current_modified = get_last_modified()
    return {'last_modified': current_modified}
```

## 3. Add JavaScript to your template

In your Jinja2 template, add this script at the bottom:

```html
<script>
let lastModified = {{ last_modified }};  // Set initial value from server

function checkForUpdates() {
    fetch('/check_updates')
        .then(response => response.json())
        .then(data => {
            if (data.last_modified > lastModified) {
                // Data changed - reload the page
                location.reload();
            }
        });
}

// Check every 5 seconds
setInterval(checkForUpdates, 5000);
</script>
```

## 4. Pass the initial timestamp to your template

When rendering your template:

```python
last_modified = get_last_modified()
template.render(your_data=data, last_modified=last_modified)
```

This will automatically refresh the whole page whenever your data changes. Want me to help adapt this to your specific server setup?
