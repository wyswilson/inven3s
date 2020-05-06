import React, { useState } from 'react';
import axios from 'axios';
import { setUserSession } from './Utils/Common';

function Login(props) {
  const [loading, setLoading] = useState(false);
  const username = useFormInput('');
  const password = useFormInput('');
  const [error, setError] = useState(null);
  // handle button click of login form
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
        props.history.push('/inventory');
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
        Username<br />
        <input type="text" {...username} autoComplete="new-password" />
      </div>
      <div style={{ marginTop: 10 }}>
        Password<br />
        <input type="password" {...password} autoComplete="new-password" />
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
