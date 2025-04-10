document.getElementById('hamburger-menu').addEventListener('click', function() {
    var dropdownMenu = document.getElementById('dropdown-menu');
    if (dropdownMenu.style.display === 'block') {
        dropdownMenu.style.display = 'none';
    } else {
        dropdownMenu.style.display = 'block';
    }
});


// Mise à jour dynamique de l'IP (exemple)
document.getElementById('ip-address').textContent = 'PR-Hub';

// Gestion du clic sur l'activité
document.getElementById('view-activity').addEventListener('click', (e) => {
  e.preventDefault();
  // Votre logique ici
  alert("Affichage de l'activité du compte");
});


