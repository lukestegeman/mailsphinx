document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('subscription-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(form);

        fetch('https://script.google.com/macros/s/AKfycbzFdJk69Qa0U5S4m-jXYG3p-xwssVpF4Dgxsm6u11OATQMBlYB2MXd-z45vZ-EO-lDj/exec', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            
            if (data.result === 'success') {
                window.location.href = 'subscribed.html';
            } else {
                alert('Error: ' + data.result);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Network error, please try again.');
        });
    });
});

