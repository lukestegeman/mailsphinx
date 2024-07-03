function getQueryParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

function deleteRow() {
    const email = getQueryParameter('email');
    const baseSite = 'https://lukestegeman.github.io/mailsphinx/'
    if (!email) {
        document.getElementById('pre').innerText = 'Email parameter missing';
        return;
    }
    const scriptURL = 'https://script.google.com/macros/s/AKfycbyfWjUxba5iWALcwK086V0yD_a5NNqPnvpRDMftJdQBR0P1tYPrB9SQuMi-qMg60n4/exec?email=' + encodeURIComponent(email);
    
    fetch(scriptURL).then(response => response.text()).then(result => {
        document.getElementById('pre').innerText = result;
        if (result === 'Row(s) deleted') {
            window.location.href = baseSite.concat("unsubscribed.html");
        }
    }).catch(error => {
        console.error('Error:', error);
        document.getElementById('pre').innerText = 'Error occurred while deleting the row';
    });
}

// Call the function on page load
window.onload = deleteRow;
