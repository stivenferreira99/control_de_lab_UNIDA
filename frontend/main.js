function login() {
    const matricula = document.getElementById('matricula').value;

    fetch('http://localhost:5000/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ matricula: matricula, id_maquina: '123' }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Contraseña generada: ' + data.password);
            // Aquí podrías implementar la lógica para desbloquear la máquina
        } else {
            alert(data.message);
        }
    });
}
