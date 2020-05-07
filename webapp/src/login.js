import React, { useState } from 'react';
import Input from './input.js';
import axios from 'axios';
import { setUserSession } from './utils/common';

function Login(props) {
  const [loading, setLoading] = useState(false);
  const username = useFormInput('');
  const password = useFormInput('');
  const [error, setError] = useState(null);


  const handleLogin = () => {
    setError(null);
    setLoading(true);
    axios.post('http://127.0.0.1:8989/user/login', {},{
       auth: {
        username: username.value,
        password: password.value
      }
    })
    .then(response => { 
      setLoading(false);
      if(response.status === 200){
        setUserSession(response.headers['access-token'],response.headers['identifier']);
        setError("login successful");
        props.history.push('/insights');
      }
    })
    .catch(error => {
      setLoading(false);
      const err_response = error.response
      if(err_response){
        if(err_response.status === 401){
          setError("login failed");
        }
        else{
          setError(err_response);
        }
      }
      else{
        setError('internal server error');
      }
    });
  }

  return (
    <div>
      Login<br /><br />
      
      <div>
        <input type="text" {...username} />
        <Input
        id={1}
        type="text"
        label="email"
        predicted=""
        locked={false}
        active={false}
        />
      </div>
      <div style={{ marginTop: 10 }}>
        <input type="password" {...password} />
        <Input
        id={1}
        type="password"
        label="password"
        predicted=""
        locked={false}
        active={false}
        />
      </div>
      {error && <><small style={{ color: 'red' }}>{error}</small><br /></>}<br />
      <input type="button" value={loading ? 'Loading...' : 'Login'} onClick={handleLogin} disabled={loading} /><br />
    </div>
  );
}

const useFormInput = initialValue => {
  const [value, setValue] = useState(initialValue);

  const handleChange = e => {
    setValue(e.target.value);
  }
  return {
    value,
    onChange: handleChange
  }
}

export default Login;
