function getQueryParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

function deleteRow() {
    const email = getQueryParameter('email');
    if (!email) {
        document.getElementById('result').innerText = 'Email parameter missing';
        return;
    }
    const scriptURL = 'https://script.google.com/macros/s/AKfycbw_K7VYWDr3j_bLVfJgrG9UGQNWU_g2znlWDuv7FusUDFl0pc2gHyYA_AeT-3O9ynmM/exec?email=' + encodeURIComponent(email);
    
    fetch(scriptURL).then(response => response.text()).then(result => {
        document.getElementById('result').innerText = result;
        if (result === 'Row(s) deleted') {
            window.location.href = 'unsubscribed.html';
        }
    }).catch(error => {
        console.error('Error:', error);
        document.getElementById('result').innerText = 'Error occurred while deleting the row';
    });
}

// Call the function on page load
window.onload = deleteRow;
