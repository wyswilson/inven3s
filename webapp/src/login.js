import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { setUserSession } from './utils/common';
import { Icon, Image, List, Header, Button, Card, Message, Grid } from 'semantic-ui-react'
import Field from './field.js';


class Login extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      apihost: 'https://inven3s.xyz',
      email: '',
      password: '',
      message: '',
      success: false,
      tried: false,
    };
  }
  
  updatecredentials(field,value) {
    if(field === 'email'){
      this.setState({ email:value });
    }
    if(field === 'password'){
      this.setState({ password:value });
    }
  }

  authenticate(event){
    this.setState({ message: 'authenticating' });
    this.setState({ tried: true });

    console.log('authenticate [' + this.state.email + ']');

    axios.post(this.state.apihost + '/user/login', {},
      {
       auth: {
        username: this.state.email,
        password: this.state.password
      }
    })
    .then(response => {
      if(response.status === 200){
        this.setState({ success: true});
        setUserSession(response.headers['access-token'],response.headers['name']);
        this.props.history.push({
          pathname: '/home',
          state: { sessionid: 'xxxxxxxxxx' }
        });
      }
    })
    .catch(error => {
      this.setState({ success: false});
      const errresponse = error.response;
      if(errresponse){
        if(errresponse.status === 401){
          this.setState({ message:'incorrect username and/or password' });
        }
        else{
          this.setState({ message:errresponse });
        }
      }
      else{
        this.setState({ message:'server unreachable' });
      }
    });
  }
  
  updatemessage(){
    if(this.state.tried){
      return (
        <Card raised>
            <Message size='tiny' warning={this.state.tried && !this.state.success}
              header={this.state.message}
            />
        </Card>
      )
    }
    else{
      return (
        <Button color="grey" className="fullwidth">
        Register interest</Button>
      )
    }
  }

  render() {
    return (
      <div>
        <div
          className={isMobile ? "bodymain login mobile" : "bodymain login"}
        >
          <Grid columns={2} doubling stackable>
            <Grid.Column textAlign="left" verticalAlign="middle">
              <Header
                content='Reducing food waste starts with your Pan3'
                className={isMobile ? "text main mobile" : "text main"}
              />
            </Grid.Column>
            <Grid.Column textAlign="center">
              <Card raised key="1" fluid>
                <Card.Content>
                  <Field label="email" type="text" active={false}
                    parentCallback={this.updatecredentials.bind(this)}/>
                  <Field label="password" type="password" active={false}
                  parentCallback ={this.updatecredentials.bind(this)}/>
                </Card.Content>
                <Card.Content extra>
                  <Grid>
                    <Grid.Column width={7}>
                      <Button color="grey" className="fullwidth" onClick={this.authenticate.bind(this)}>
                      Login</Button>
                    </Grid.Column>
                    <Grid.Column width={8}>
                      {this.updatemessage()}
                    </Grid.Column>
                  </Grid>
                </Card.Content>
              </Card> 
            </Grid.Column>
          </Grid>
        </div>
        <div 
          className={isMobile ? "bodyrest1 login mobile" : "bodyrest1 login"}
        >
          <Grid celled='internally' columns='equal' stackable>
            <Grid.Row textAlign='left'>
              <Grid.Column className="fontdark">
                <Header as='h3' style={{ fontSize: '1.8em' }} className="fontdark">
                  What are we solving?
                </Header>
                <p style={{ fontSize: '1.1em' }} className="fontdark">
                  Aussie households throw away <a href="https://www.foodwise.com.au/foodwaste/food-waste-fast-facts/" target="_blank" rel="noopener noreferrer">3 average-size fridges</a> worth of food per household each year
                </p>
              </Grid.Column>
              <Grid.Column verticalAlign="middle">

                <List floated="left" className="fontdark">
                  <List.Item icon='barcode' content="Mistakenly throwing out food due to confusion with the used-by date" />
                  <List.Item icon='barcode' content="Buying more than what we need by not checking our pantry before shopping and not sticking to shopping list" />
                  <List.Item icon='barcode' content="Not knowing how to make the best use of the food that we have at home" />
                </List>
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </div>
        <div 
          className={isMobile ? "bodyrest2 login mobile" : "bodyrest2 login"}
        >
          <Grid celled='internally' columns='equal' stackable>
            <Grid.Row textAlign='left'>
              <Grid.Column>
                <Header as='h3' style={{ fontSize: '1.8em' }} className="fontlight">
                  How are we solving it?
                </Header>
                <p style={{ fontSize: '1.1em' }} className="fontlight">
                  By tracking and better managing food items we have at home using AI to minimise waste and save you time
                </p>
              </Grid.Column>
              <Grid.Column verticalAlign="middle">
                <List floated="left" className="fontlight">
                  <List.Item icon='barcode' content="Reminds you of expiring food so that you can prioritise consuming them sooner" />
                  <List.Item icon='barcode' content="Writes your shopping lists for you with food that are running out or that you likely need" />
                  <List.Item icon='barcode' content="Suggests recipes you can make using the food that you have at home" />
                </List>
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </div>
        <div className={isMobile ? "navfooter login mobile" : "navfooter login"}>
          <List horizontal verticalAlign="middle">
            <List.Item className="footheader">
              <Image src='/logolonglight.png' size='tiny' inline verticalAlign="middle" /> Copyright © 2020 Inven3s. All Rights Reserved.
            </List.Item>
            <List.Item className="footheader">
              <a href="https://www.instagram.com/inven3s/" target="_blank" rel="noopener noreferrer"><Icon name="instagram" size="large" /></a>
            </List.Item>
          </List>
        </div>
      </div>
    )
  }
}
export default Login;
