import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken } from './utils/common';
import { Label, Message, Modal, Grid, Dropdown, Input, List, Button, Image } from 'semantic-ui-react'
import { DateInput } from 'semantic-ui-calendar-react';
import _ from 'lodash'

class ToBuy extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      //apihost: 'http://127.0.0.1:88',
      apihost: 'https://inven3s.xyz',
      token: getToken(),
      loading: false,
      actionedmsg: '',
      defaultimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      slist:[],
      retailersuggests:[],
      gtin:'',
      retailerid:'',
      retailername:'',
      quantity:1,
      dateexpiry:''
    };
  }

  lookupretailer(event, data){
    const retailer = data.searchQuery

    if(retailer.length > 3){
      this.searchretailers(retailer);
    }
  }

  searchretailers(retailer){
    console.log('searchretailers [' + retailer + ']');
   
    axios.get(this.state.apihost + '/retailer/' + retailer,
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          console.log('searchretailers [' + response.data[0]['message'] + ']');
          
          this.updateretailersuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          if(error.response.data){
            console.log('searchretailers [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
          }
          else{
            console.log('searchretailers [server unreachable]');   
          }
        }
        else{
          console.log('searchretailers [server unreachable]');
        }
      });
  }

  updateretailersuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.retailerid,
          text: item.retailername,
          value: item.retailername,
        }
      ));
    this.setState({ retailersuggests: updatedsuggest });
  }

  addnewretailer(event,data){
    this.setState({ actionedmsg: '' });
    this.setState({ loading: true });

    const newretailer = data.value;
    console.log('addnewretailer [' + newretailer + ']');

    axios.post(this.state.apihost + '/retailer', 
      {
        retailername: newretailer
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
        console.log('addnewretailer [' + response.data[0]['message'] + ']');
        this.setState({ actionedmsg: response.data[0]['message'] });

        this.setState({ retailerid: response.data[0]['results'][0]['retailerid'] });
        this.setState({ retailername: response.data[0]['results'][0]['retailername']  });
        this.updateretailersuggests(response.data[0]['results']);
      }
    })
    .catch(error => {
      this.setState({ loading: false });
      if(error.response){
        if(error.response.data){
          console.log('addnewretailer [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
          this.setState({ actionedmsg: error.response.data[0]['message'] });        
        }
        else{
          console.log('addnewretailer [server unreachable]');
          this.setState({ actionedmsg: 'server unreachable' });
        }
      }
      else{
        console.log('addnewretailer [server unreachable]');
        this.setState({ actionedmsg: 'server unreachable' });
      }
    });        
  }

  setproductmetadata(event, gtin){
    this.setState({ gtin: gtin });
    this.setState({ actionedmsg: ''});
  }

  setinventorymetadata(event, data){
    const field = data.name;
    const value = data.value;
    console.log('setinventorymetadata [' + field + ':' + value + ']');

    if(field === 'retailername'){
      const array = this.state.retailersuggests;
      let selectedarr = array.filter(prod => prod.value.includes(value))[0];
      if(selectedarr){
        const selectedid = selectedarr['key'];
        this.setState({ retailerid: selectedid });
        this.setState({ retailername: value });
      }
      else{
        //NEw RETAILER
      }
    }
    else if(field === 'quantity'){
      this.setState({ quantity: value });
    }
    else if(field === 'dateexpiry'){
      this.setState({ dateexpiry: value });
    }
  }

  addinventory(gtin){
    this.setState({ actionedmsg: '' });
    this.setState({ loading: true });

    console.log('addinventory [' + gtin + ']');

    axios.post(this.state.apihost + '/inventory', 
      {
        gtin:gtin,
        retailername:this.state.retailername,
        dateexpiry:this.state.dateexpiry,
        quantity:this.state.quantity,
        itemstatus:'IN',
        receiptno:'',
        queryisedible:'2',
        queryisopened:'2',
        queryexpirystatus:'all'
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
        console.log('addinventory [' + response.data[0]['message'] + ']');
        this.setState({ actionedmsg: response.data[0]['message'] });

        this.setState({ gtin: '' });
        this.setState({ retailerid: ''});
        this.setState({ retailername: ''});
        this.setState({ dateexpiry: ''});
        this.setState({ quantity: 1 });

        this.fetchshoppinglist();
      }
    })
    .catch(error => {
      this.setState({ loading: false });
      if(error.response){
        if(error.response.data){
          console.log('addinventory [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
          this.setState({ actionedmsg: error.response.data[0]['message'] });        
        }
        else{
          console.log('addinventory [server unreachable]');
          this.setState({ actionedmsg: 'server unreachable' });
        }
      }
      else{
        console.log('addinventory [server unreachable]');
        this.setState({ actionedmsg: 'server unreachable' });
      }
    });
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
        
        const updatedlist = _.map(response.data[0]['results'], (item) => (
          {
            gtin: item.gtin,
            productname: item.productname,
            productimage: item.productimage,
            productimagelocal: item.productimagelocal,
            brandname: item.brandname,
            isedible: item.isedible,
            isfavourite: item.isfavourite,
            retailers: item.retailers.split(',').map( (retailer) => (
                <Label key={item.gtin + retailer} basic size='medium' className='margined' content={retailer}/>
              ))
          }
        ));
        this.setState({ slist: updatedlist });
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

  redirectoproduct(gtin, productname, productimage, productimagelocal, brandname, isedible, isfavourite){
    this.props.history.push({
      pathname: '/product',
      state: { gtin: gtin, productname: productname, productimage: productimage, productimagelocal: productimagelocal, brandname: brandname, isedible: isedible, isfavourite: isfavourite }
    })
  }

  generateitemadditionmsg(){
      if(this.state.actionedmsg !== ''){
        return (
          <Message className="fullwidth" size="tiny">{this.state.actionedmsg}</Message>
        )
      }
  }

  componentDidMount() {
    this.fetchshoppinglist();
  }

  generateshoppinglist(){
    return this.state.slist.map( (item) => (
            <List.Item key={item.gtin}>
              <List.Content floated='right'>
                <Modal
                      trigger={<Button icon="plus" className='grey button'
                      onClick={this.setproductmetadata.bind(this,item.gtin)} />}
                      centered={false}
                      size="fullscreen"
                      dimmer="blurring"
                      closeIcon
                    >
                  <Modal.Header>Add items</Modal.Header>
                  <Modal.Content image>
                    <Image
                      wrapped size='tiny' src={item.productimagelocal}
                      onError={(e)=>{e.target.onerror = null; e.target.src=item.productimage}}
                    />
                    <Modal.Description>
                      <Grid columns={1} doubling stackable>
                        <Grid.Column>
                         <label className="fullwidth">Retailer</label>                    
                          <Dropdown className="fullwidth" name="retailername"
                            search
                            selection
                            allowAdditions
                            value={this.state.retailername}
                            noResultsMessage="No retailer found"
                            options={this.state.retailersuggests}
                            onSearchChange={this.lookupretailer.bind(this)}
                            onAddItem={this.addnewretailer.bind(this)}
                            onChange={this.setinventorymetadata.bind(this)}
                          />
                        </Grid.Column>
                        <Grid.Row columns={2}>
                          <Grid.Column>
                            <label className="fullwidth">Quantity</label>                    
                            <Input className="fullwidth" name="quantity"
                              value={this.state.quantity}
                              onChange={this.setinventorymetadata.bind(this)}
                            />
                          </Grid.Column>
                          <Grid.Column>
                            <label className="fullwidth">Expiry</label>                    
                            <DateInput name="dateexpiry" className="fullwidth"
                              dateFormat="YYYY-MM-DD"
                              value={this.state.dateexpiry}
                              onChange={this.setinventorymetadata.bind(this)}
                            />
                          </Grid.Column>
                        </Grid.Row>
                      </Grid>
                    </Modal.Description>
                  </Modal.Content>
                  <Modal.Actions>
                    <Grid columns={2} container doubling stackable>
                      <Grid.Column>
                        <Button loading={this.state.loading || false} 
                        className='grey button fullwidth'
                        onClick={this.addinventory.bind(this,item.gtin)}>
                          ADD
                        </Button>
                      </Grid.Column>
                      <Grid.Column>
                        {this.generateitemadditionmsg()}
                      </Grid.Column>
                    </Grid>
                  </Modal.Actions>
                </Modal>
              </List.Content>
              <List.Content floated='left'>
                <Image
                  size="tiny" src={item.productimagelocal}
                  onError={(e)=>{e.target.onerror = null; e.target.src=item.productimage}}
                />
              </List.Content>
              <List.Content>
                <List.Header as="a" onClick={this.redirectoproduct.bind(this,item.gtin,item.productname,item.productimage,item.productimagelocal, item.brandname, item.isedible, item.isfavourite)}>{item.productname}</List.Header>
                <List.Description>{item.retailers}</List.Description>
              </List.Content>
            </List.Item>
           ));
  }

  render() {
    return (
      <div
        className={isMobile ? "bodymain mobile" : "bodymain"}
      >
        <List divided celled relaxed floated="left" size="medium" className='fullwidth'>
          {this.generateshoppinglist()}
        </List>
      </div>
    )
  }
}
export default ToBuy;

