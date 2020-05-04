// UserDetails.jsx
import React, { Component } from 'react';
import { Form, Button } from 'semantic-ui-react';

class UserDetails extends Component{

    authenticate = (e) => {
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'username':'wyswilson@live.com',
                'password':'siaosiao' })
        };

        return fetch('http://127.0.0.1:8989/login', requestOptions)
            .then(handleResponse)
            .then(user => {
                // login successful if there's a user in the response
                if (user) {
                    console.log('successful')

                    // store user details and basic auth credentials in local storage 
                    // to keep user logged in between page refreshes
                    user.authdata = window.btoa(username + ':' + password);
                    localStorage.setItem('user', JSON.stringify(user));
                }

                return user;
            });
    }

    render(){
        const { values } = this.props;
        return(
            <Form >
                <h1 className="ui centered">Login</h1>
                <Form.Field>
                    <label>Email</label>
                    <input
                    placeholder='email'
                    onChange={this.props.handleChange('email')}
                    defaultValue={values.email}
                    />
                </Form.Field>
                <Button onClick={this.authenticate}>Login</Button>
            </Form>
        )
    }
}

export default UserDetails;