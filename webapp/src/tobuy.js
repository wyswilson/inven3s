import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken } from './utils/common';
import { List, Button, Image } from 'semantic-ui-react'


class ToBuy extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      //apihost: 'http://127.0.0.1:88',
      apihost: 'https://inven3s.xyz',
      token: getToken(),
      loading: false,
      actionedmsg: '',
      actioned: false,
      slist:[]
    };
  }

  fetchshoppinglist(){
    console.log('fetchshoppinglist');
   
    axios.get(this.state.apihost + '/shoppinglist',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        console.log('shoppinglist [' + response.data[0]['message'] + ']');
        
        this.setState({ slist: response.data[0]['results'] });
      }
    })
    .catch(error => {
      this.setState({ inventoryfetched: false });
      if(error.response){
        if(error.response.status === 404){
          console.log('shoppinglist [' + error.response.data[0]['message'] + ']');        
         }
        else{
          console.log('shoppinglist [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
        }
      }
      else{
        console.log('fetchinventory [server unreachable]');
        this.setState({ inventorymsg: 'server unreachable' })
      }
    });
  }
  
  additemtoinventory(){

  }

  componentDidMount() {
    this.fetchshoppinglist();
  }

  generateshoppinglist(){
    return this.state.slist.map( (item) => (
            <List.Item key={item.gtin}>
              <List.Content floated='right'>
                <Button icon="plus" color="grey" onClick={this.additemtoinventory.bind(this,item.gtin)} />
              </List.Content>
              <List.Content floated='left'>
                <Image size="tiny" src={item.productimage} />
              </List.Content>
              
              <List.Content>
                <List.Header>{item.productname}</List.Header>
                <List.Description as='a'>{item.retailers}</List.Description>
              </List.Content>
            </List.Item>
           ));
  }

  render() {
    return (
      <div
        className={isMobile ? "bodymain mobile" : "bodymain"}
      >
        <List divided celled floated="left">
          {this.generateshoppinglist()}
        </List>
      </div>
    )
  }
}
export default ToBuy;

