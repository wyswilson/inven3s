import React from 'react';
import axios from 'axios';
import { setUserSession } from './utils/common';
import { Popup, Icon, List, Header, Button, Card, Message, Grid, Image } from 'semantic-ui-react'
import Field from './field.js';
import _ from 'lodash'
import {isMobile} from 'react-device-detect';

import scrollToComponent from 'react-scroll-to-component';

class Login extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      //apihost: 'http://127.0.0.1:88',
      apihost: 'https://inven3s.xyz',
      loading: false,
      email: '',
      password: '',
      interestemail: '',
      message: '',
      messageactive: false,
      interestmessage: '',
      topproducts: null,
      allproductscnt: 'a large number of'
    };
  }
  
  updatecredentials(field,value) {
    if(field === 'Email'){
      this.setState({ email:value });
    }
    if(field === 'Password'){
      this.setState({ password:value });
    }
  }

  loadtopproducts(products){
    const prodgrid = _.map(products, (item) => (
        <Grid.Column key={item.gtin}>
          <Card raised key={item.gtin}>
            <Card.Content textAlign="center">
              <Image inline wrapped src={item.productimagelocal}
                size='tiny'                   
                onError={(e)=>{e.target.onerror = null; e.target.src=item.productimage}}
              />
              <Card.Header className="item title" textAlign="center">{item.productname}</Card.Header>
            </Card.Content>
          </Card>
        </Grid.Column>
      ));
    this.setState({topproducts: prodgrid});
  }

  componentDidMount() {
    this.fetchtopproducts();
  }

  fetchproductscnt(){
    console.log('fetchproductscnt');
   
    axios.get(this.state.apihost + '/public/productscnt')
    .then(response => { 
      if(response.status === 200){
        console.log('fetchproductscnt [' + response.data[0]['message'] + ']');
        this.setState({ allproductscnt: response.data[0]['count']});
      }
    })
    .catch(error => {
      if(error.response){
        console.log('fetchproductscnt [' + error.response.data[0]['message'] + ']');
      }
      else{
        console.log('fetchproductscnt [server unreachable]');
      }
    });
  }

  fetchtopproducts(){
    console.log('fetchtopproducts');
   
    axios.get(this.state.apihost + '/public/topproducts')
    .then(response => { 
      if(response.status === 200){
        console.log('fetchtopproducts [' + response.data[0]['message'] + ']');
        this.loadtopproducts(response.data[0]['results']);
        this.fetchproductscnt();
      }
    })
    .catch(error => {
      if(error.response){
        console.log('fetchtopproducts [' + error.response.data[0]['message'] + ']');
      }
      else{
        console.log('fetchtopproducts [server unreachable]');
      }
    });
  }

  updateinterest(field,value){
    this.setState({ interestemail: value });
  }

  registerinterest(event){
    this.setState({ loading: true });

    axios.post(this.state.apihost + '/public/userinterest', 
      {
        email:this.state.interestemail
      }, 
      {
        headers: {
          'crossDomain': true,
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => {
      this.setState({ loading: false });
      if(response.status === 200){
        this.setState({ interestmessage: response.data[0]['message'] });
      }
    })
    .catch(error => {
      this.setState({ loading: false });
      const errresponse = error.response;
      if(errresponse){
        this.setState({ interestmessage: errresponse.data[0]['message'] });
      }
      else{
        this.setState({ interestmessage: 'Unable to reach server. Please try again later.' });
      }
    });
  }

  generateinterestmessage(){
    if(this.state.interestmessage !== ''){
      return (<Message className="fullwidth" size="tiny">
          {this.state.interestmessage}</Message>
        );
    }
  }

  authenticate(event){
    this.setState({ messageactive: true });
    if(this.state.email !== '' && this.state.password !== ''){
      this.setState({ message: 'authenticating' });

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
          setUserSession(response.headers['access-token'],response.headers['name']);
          this.props.history.push({
            pathname: '/home',
            state: { sessionid: 'xxxxxxxxxx' }
          });
        }
        else{
          this.setState({ message:'unknown error' });
        }
      })
      .catch(error => {
        const errresponse = error.response;
        if(errresponse){
          if(errresponse.status === 401){
            this.setState({ message:'incorrect username and/or password' });
          }
          else{
            this.setState({ message: 'server unreachable' });
          }
        }
        else{
          this.setState({ message:'server unreachable' });
        }
      });
    }
    else{
      this.setState({ message: 'require username and password' });
    }
  }
  
  scrollto(event){
    scrollToComponent(this.registerinterestpanel);
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
                content='Reducing food waste starts with your inventory'
                className={isMobile ? "text main mobile" : "text main"}
              />
            </Grid.Column>
            <Grid.Column textAlign="center">
              <Card raised key="1" fluid>
                <Card.Content>
                  <Field label="Email" type="text" active={false}
                    parentCallback={this.updatecredentials.bind(this)}/>
                  <Field label="Password" type="password" active={false}
                  parentCallback ={this.updatecredentials.bind(this)}/>
                </Card.Content>
                <Card.Content extra>
                  <Grid>
                    <Grid.Column width={8}>
                      <Popup
                        content={this.state.message}
                        mouseLeaveDelay={500}
                        on='hover'
                        disabled={!this.state.messageactive}
                        trigger={
                          <Button className='kuning button fullwidth' onClick={this.authenticate.bind(this)}>
                          LOGIN</Button>
                        }
                      />
                    </Grid.Column>
                    <Grid.Column width={8}>
                      <Button className='kuning button fullwidth'
                      onClick={this.scrollto.bind(this)}>
                      REGISTER INTEREST</Button>
                    </Grid.Column>
                  </Grid>
                </Card.Content>
              </Card> 
            </Grid.Column>
          </Grid>
        </div>
        <div 
          className={isMobile ? "bodyrest2 login mobile" : "bodyrest2 login"}
        >
          <Grid celled='internally' columns='equal' stackable>
            <Grid.Row textAlign='left'>
              <Grid.Column className="fontdark">
                <Header as='h3' style={{ fontSize: '24px' }} className="fontdark">
                  Food waste is a problem
                </Header>
                <p className="fontdark">
                  Aussie households throw away 3 average-size fridges worth of food each year <a href="https://www.foodwise.com.au/foodwaste/food-waste-fast-facts/" target="_blank" rel="noopener noreferrer" style={{color: "#ffffff"}}>[1]</a>, which is both bad for the environment and your pocket
                </p>
              </Grid.Column>
              <Grid.Column verticalAlign="middle">
                <List floated="left" className="fontdark">
                  <List.Item icon='barcode' content="Mistakenly throwing out food due to confusion with the used-by date" />
                  <List.Item icon='barcode' content="Buying more than what we need by not checking our inventory before shopping and not sticking to shopping list" />
                  <List.Item icon='barcode' content="Not knowing how to make the best use of the food that we have at home" />
                </List>
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </div>
        <div 
          className={isMobile ? "bodyrest1 login mobile" : "bodyrest1 login"}
        >
          <Grid celled='internally' columns='equal' stackable>
            <Grid.Row textAlign='left'>
              <Grid.Column>
                <Header as='h3' style={{ fontSize: '24px' }} className="fontlight">
                  How does our technology help?
                </Header>
                <p className="fontlight">
                Our web app enables effortless tracking of food items when you are at home or on-the-go and uses AI to help you manage them to reduce waste and save you time
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
        <div 
          className={isMobile ? "bodyrest2 login mobile" : "bodyrest2 login"}
        >
          <Grid celled='internally' columns='equal' stackable>
            <Grid.Column>
              <Header as='h3' style={{ fontSize: '24px' }} className="fontdark">
              Recent top products in inventories
              </Header>
              <p className="fontdark">
                We have {this.state.allproductscnt} unique products in our inventories and the number is growing
              </p>
              <Grid doubling stackable>
                <Grid.Row stretched columns={5}>
                  {this.state.topproducts}
                </Grid.Row>
              </Grid>
            </Grid.Column>
          </Grid>
        </div>        
        <div 
          className={isMobile ? "bodyrest1 login mobile" : "bodyrest1 login"}
          ref={(div) => { this.registerinterestpanel = div; }}
        >
          <Grid celled='internally' columns='equal' stackable>
            <Grid.Column className="fontlight">
              <Header as='h3' style={{ fontSize: '24px' }} className="fontlight">
                Ready to make a difference?
              </Header>
              <p className="fontlight">
                Want to find out more or interested in early access to the web app? Let us know and we'll get back to you
              </p>
            </Grid.Column>
            <Grid.Column verticalAlign="middle">
              <Grid columns={1} doubling stackable>
                <Grid.Column>
                  <Field label="Enter email address" type="text" active={false}
                  parentCallback={this.updateinterest.bind(this)}/>
                </Grid.Column>
                <Grid.Row columns={2}>
                  <Grid.Column width={7}>
                    <Button className='kuning button fullwidth'
                      loading={this.state.loading || false}
                      onClick={this.registerinterest.bind(this)}>
                      REGISTER NOW</Button>
                  </Grid.Column>
                  <Grid.Column width={9}>
                    {this.generateinterestmessage()}
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Grid.Column>
          </Grid>
        </div>
        <div className={isMobile ? "navfooter login mobile" : "navfooter login"}>
          <List horizontal verticalAlign="middle">
            <List.Item className="footheader">
              Copyright © 2020 Inven3s. All Rights Reserved.
            </List.Item>
            <List.Item className="footheader">
              <a href="https://www.instagram.com/inven3s/" target="_blank" rel="noopener noreferrer" className="footheader"><Icon name="instagram" size="large" /></a>
            </List.Item>
          </List>
        </div>
      </div>
    )
  }
}
export default Login;
