import React, { useState } from "react";
import axios from "axios";

const Login = ({ setToken }) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post("http://localhost:5000/api/login", {
                username,
                password,
            });

            const token = response.data.access_token;
            setToken(token);
            localStorage.setItem("token", token);
        } catch (err) {
            setError("Credenciales incorrectas");
        }
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>Iniciar Sesión</h2>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <form onSubmit={handleLogin}>
                <input
                    type="text"
                    placeholder="Usuario"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <br />
                <input
                    type="password"
                    placeholder="Contraseña"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <br />
                <button type="submit">Ingresar</button>
            </form>
        </div>
    );
};

export default Login;
