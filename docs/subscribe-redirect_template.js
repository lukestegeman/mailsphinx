document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('subscription-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(form);

        fetch('${googleScriptURL}$', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            
            if (data.result === 'success') {
                window.location.href = 'subscribed.html';
            } else {
                alert('Error: ' + data.error);
                form.reset();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Network error, please try again.');
        });
    });
});

