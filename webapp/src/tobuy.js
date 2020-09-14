import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken } from './utils/common';
import { Menu, Card, Tab, Label, Message, Modal, Grid, Dropdown, Input, List, Button, Image } from 'semantic-ui-react'
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
      hasshoppinglist: false,
      loadingshopping: false,
      defaultimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      slist:[],
      slistbycat:[],
      activecat:0,
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
        queryexpirystatus:'all',
        querycategory:'all'
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

        this.fetchshoppinglistbycat();
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
      
  fetchshoppinglistbycat(){
    this.setState({ loadingshopping: true});
    this.setState({ hasshoppinglist: false});
    console.log('fetchshoppinglistbycat');
   
    axios.get(this.state.apihost + '/shoppinglist/categories',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      this.setState({ loadingshopping: false});
      console.log('fetchshoppinglistbycat [' + response.data[0]['message'] + ']');

      this.setState({ slistbycat: response.data[0]['results'] });
      this.setState({ hasshoppinglist: true});
    })
    .catch(error => {
      this.setState({ loadingshopping: false});
      console.log('fetchshoppinglistbycat [server unreachable]');
    });
  }

  fetchshoppinglist(){
    this.setState({ loadingshopping: true});
    this.setState({ hasshoppinglist: false});
    console.log('fetchshoppinglist');
   
    axios.get(this.state.apihost + '/shoppinglist/items',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
     if(response.status === 200){
        console.log('fetchshoppinglist [' + response.data[0]['message'] + ']');
        
        const updatedlist = _.map(response.data[0]['results'], (item) => (
          {
            gtin: item.gtin,
            productname: item.productname,
            productimage: item.productimage,
            productimagelocal: item.productimagelocal,
            brandname: item.brandname,
            isedible: item.isedible,
            isfavourite: item.isfavourite,
            categories: item.categories,
            retailers: item.retailers.split(',').map( (retailer) => (
                <Label key={item.gtin + retailer} basic size='medium' className='margined' content={retailer}/>
              ))
          }
        ));
        this.setState({ slist: updatedlist });
        this.setState({ hasshoppinglist: true});
      }
      this.setState({ loadingshopping: false});
    })
    .catch(error => {
      this.setState({ hasshoppinglist: false });
      if(error.response){
        if(error.response.status === 404){
          console.log('fetchshoppinglist [' + error.response.data[0]['message'] + ']');        
         }
        else{
          console.log('fetchshoppinglist [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
        }
      }
      else{
        console.log('fetchshoppinglist [server unreachable]');
        this.setState({ inventorymsg: 'server unreachable' });
      }
      this.setState({ loadingshopping: false});
    });
  }

  redirectoproduct(gtin, productname, productimage, productimagelocal, brandname, isedible, isfavourite, categories){
    this.props.history.push({
      pathname: '/products',
      state: { gtin: gtin, productname: productname, productimage: productimage, productimagelocal: productimagelocal, brandname: brandname, isedible: isedible, isfavourite: isfavourite, categoryoptions: categories }
    })
  }

  generateitemadditionmsg(){
      if(this.state.actionedmsg !== ''){
        return (
          <Message className="fullwidth" size="tiny">{this.state.actionedmsg}</Message>
        )
      }
  }

  switchcat(event,selected){
    const selectedindex = selected.index;
    if(selectedindex === this.state.activecat){
      this.setState({ activecat: 0});
    }
    else{
      this.setState({ activecat: selected.index});

    }
  }

  componentDidMount() {
    //this.fetchshoppinglist();
    this.fetchshoppinglistbycat();
  }

  generateshoppinglistbycat(){
    if(!this.state.loadingshopping && this.state.hasshoppinglist){
      let panes = [];
      this.state.slistbycat.forEach(function(item) {
        let pane = {};
        pane['menuItem'] = (<Menu.Item key={item.name} >
                              {item.name}<Label size='mini' attached='top right'>{item.count}</Label>
                            </Menu.Item>
                          );

        const render = () => {
          return (
            <Tab.Pane attached={true}>
              <Card.Group doubling itemsPerRow={3} stackable>
                {item.items.map(proditem => (
                  <Card raised key={proditem.gtin}>
                    <Card.Content textAlign="center">
                      <Image src={proditem.productimagelocal}
                        size='tiny' style={{padding: '10px', width: 'auto', height: '80px'}}                  
                        onError={(e)=>{e.target.onerror = null; e.target.src=proditem.productimage}}
                      />
                      <Card.Header className="item title">{proditem.productname}</Card.Header>
                      <Label className={proditem.isfavourite === 1 ? 'kuning button' : 'grey button'} attached='top right'>{proditem.itemstotal}</Label>
                    </Card.Content>
                    <Card.Content extra textAlign="center">
                      <div className='ui two buttons'>
                        <Button icon="edit" className={proditem.isfavourite === 1 ? 'kuning button' : 'grey button'} onClick={this.redirectoproduct.bind(this,proditem.gtin,proditem.productname,proditem.productimage,proditem.productimagelocal, proditem.brandname, proditem.isedible, proditem.isfavourite, proditem.categories)} />
                        <Modal
                              trigger={<Button icon="plus" fluid className={proditem.isfavourite === 1 ? 'kuning button' : 'grey button'}
                              onClick={this.setproductmetadata.bind(this,item.gtin)} />}
                              centered={false}
                              size="fullscreen"
                              dimmer="blurring"
                              closeIcon
                        >
                          <Modal.Header>Add items</Modal.Header>
                          <Modal.Content image>
                            <Image
                              wrapped size='tiny' src={proditem.productimagelocal}
                              onError={(e)=>{e.target.onerror = null; e.target.src=proditem.productimage}}
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
                                onClick={this.addinventory.bind(this,proditem.gtin)}>
                                  ADD
                                </Button>
                              </Grid.Column>
                              <Grid.Column>
                                {this.generateitemadditionmsg()}
                              </Grid.Column>
                            </Grid>
                          </Modal.Actions>
                        </Modal>
                      </div>
                    </Card.Content>
                  </Card>
                ))}
              </Card.Group>
            </Tab.Pane>
          );
        };
        pane['render'] = render;

        
        panes.push(pane);
      },this);

      return (
          <Tab 
            menu={{ fluid: true, vertical: true }}
            menuPosition='left'
            panes={panes}
          />
      );
    }
    else if(this.state.loadingshopping){
      return (<div>
              <b>Loading your inventory.</b><br/>
                Please try again later if it doesn't load.
              </div>
          );
    }
    else{
      return (<div>
              <b>No shopping list available.</b><br/>
                Start tracking items that go in and out of your inventory.
              </div>
              );    
    }
  }

  generateshoppinglist(){
    if(!this.state.loadingshopping && this.state.hasshoppinglist){
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
                <List.Header as="a" onClick={this.redirectoproduct.bind(this,item.gtin,item.productname,item.productimage,item.productimagelocal, item.brandname, item.isedible, item.isfavourite, item.categories)}>{item.productname}</List.Header>
                <List.Description>{item.retailers}</List.Description>
              </List.Content>
            </List.Item>
         ));
    }
    else if(this.state.loadingshopping){
      return (<List.Item key={0}>
                <List.Content floated='left'>
                  <List.Header>Loading your inventory.</List.Header>
                  Please try again later if it doesn't load.
                </List.Content>
              </List.Item>
              );
    }
    else{
      return (<List.Item key={0}>
                <List.Content floated='left'>
                  <List.Header>No shopping list available.</List.Header>
                  Start tracking items that go in and out of your inventory.
                </List.Content>
              </List.Item>
              );      
    }
  }

  render() {
    return (
      <div
        className={isMobile ? "bodymain mobile" : "bodymain"}
      >
        {this.generateshoppinglistbycat()}
      </div>
    )
  }
}
export default ToBuy;

