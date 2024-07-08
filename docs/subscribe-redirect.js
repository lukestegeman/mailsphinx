document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('subscription-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(form);

        fetch('https://script.google.com/macros/s/AKfycbwMmo6bxNodmL_A9smMaSsvOxhdGEsNerjFIQ7pmpmVQ2_2W_WPgLjBfyc7ZFeWI9qw/exec', {
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

