import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken } from './utils/common';
import { Icon, Message, Grid, Dropdown, Modal, Button, Input, Label, Card, Image  } from 'semantic-ui-react'
import { DateInput } from 'semantic-ui-calendar-react';
import _ from 'lodash'

class Pan3 extends React.Component {
  constructor(props) {
    super(props)
    const redirectstate = this.props.location.state;
    //const querystr = queryString.parse(this.props.location.search);
    this.state = {
      //apihost: 'http://127.0.0.1:88',
      apihost: 'https://inven3s.xyz',
      token: getToken(),
      loading: false,
      actionedmsg: '',
      inventoryfetched: false,
      inventorymsg: '',
      inventoryfilterable: false,
      queryisedible: redirectstate ? redirectstate.queryisedible : '2',
      //queryisedible: querystr ? querystr.isedible : '2',
      queryisopened: redirectstate ? redirectstate.queryisopened : '2',
      //queryisopened: querystr ? querystr.isopened : '2',
      queryexpirystatus: redirectstate ? redirectstate.queryexpirystatus : 'all',
      defaultimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      gtin: '',
      productname: '',
      productimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      productimagelocal: 'https://react.semantic-ui.com/images/wireframe/image.png',
      brandid:'',
      brandname:'',
      retailerid:'',
      retailername:'',
      inventory:[],
      dateexpiry:'',
      quantity: 1,
      productsuggests: [],
      retailersuggests: []
    };
  }

  fetchinventory(){
    console.log('fetchinventory');
    this.setState({ inventoryfetched: false });
   
    axios.get(this.state.apihost + '/inventory?isedible=' + this.state.queryisedible + '&isopened=' + this.state.queryisopened + '&expirystatus=' + this.state.queryexpirystatus,
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        console.log('fetchinventory [' + response.data[0]['message'] + ']');
        this.setState({ inventorymsg: this.generatecountmsg(response.data[0]['count']) });
        this.setState({ inventoryfetched: true });
        
        this.setState({ inventory: response.data[0]['results'] });
      }
    })
    .catch(error => {
      if(error.response){
        if(error.response.status === 404){
          console.log('fetchinventory [' + error.response.data[0]['message'] + ']');        
          this.setState({ inventorymsg: 'no items matching the criteria' })
          this.setState({ inventoryfetched: true });
        }
        else{
          console.log('fetchinventory [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
          this.setState({ inventorymsg: error.response.data[0]['message'] })
        }
      }
      else{
        console.log('fetchinventory [server unreachable]');
        this.setState({ inventorymsg: 'server unreachable' })
      }
    });
  }

  generatecountmsg(itemcnt){
    let message = itemcnt;
    this.setState({ inventoryfilterable: true });
    if(this.state.queryisedible === 0 && this.state.queryisopened === 0){
      message += " new non-food items";
    }
    else if(this.state.queryisedible === 0 && this.state.queryisopened === 1){
      message += " opened non-food items";
    }
    else if(this.state.queryisedible === 1 && this.state.queryisopened === 0){
      message += " new food items";
    }
    else if(this.state.queryisedible === 1 && this.state.queryisopened === 1){
      message += " opened food items";
    }
    else if(this.state.queryexpirystatus !== 'all'){
      message += " " + this.state.queryexpirystatus + " items";          
    }
    else{
      this.setState({ inventoryfilterable: false });
      message += ' items';
    }

    return message
  }

  componentDidMount() {
    this.fetchinventory();
  }

  lookupproduct(event, data){
    const gtinorproduct = data.searchQuery

    if(gtinorproduct.length > 3){
      this.searchproducts(gtinorproduct);
    }
  }

  searchproducts(gtinorproduct){
    console.log('searchproducts [' + gtinorproduct + ']');

    axios.get(this.state.apihost + '/product/' + gtinorproduct + '?isedible=2',
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          console.log('searchproducts [' + response.data[0]['message'] + ']');
          this.updateproductsuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          if(error.response.data){
            console.log('searchproducts [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
          }
          else{
            console.log('searchproducts [server unreachable]');
          }
        }
        else{
          console.log('searchproducts [server unreachable]');
        }
      });
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

  setinventorymetadata(event, data){
    const field = data.name;
    const value = data.value;
    console.log('setinventorymetadata [' + field + ':' + value + ']');

    if(field === 'productname'){
      const array = this.state.productsuggests;
      let selectedarr = array.filter(prod => prod.value.includes(value))[0];

      if(selectedarr){
        const selectedgtin = selectedarr['key'];
        const selectedimg = selectedarr['img'];
        const selectedimglocal = selectedarr['imglocal'];

        this.setState({ gtin: selectedgtin });
        this.setState({ productname: value });
        this.setState({ productimage: selectedimg });
        this.setState({ productimagelocal: selectedimglocal });
      }
      else{
        //NEW PRODCU
      }
    }
    else if(field === 'retailername'){
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
        queryisedible:this.state.queryisedible,
        queryisopened:this.state.queryisopened,
        queryexpirystatus:this.state.queryexpirystatus
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

        this.setState({ inventory: response.data[0]['results'] });
        this.setState({ gtin: '' });
        this.setState({ productname: '' });
        this.setState({ productimage: 'https://react.semantic-ui.com/images/wireframe/image.png' });
        this.setState({ productimagelocal: 'https://react.semantic-ui.com/images/wireframe/image.png' });
        this.setState({ retailerid: ''});
        this.setState({ retailername: ''});
        this.setState({ dateexpiry: ''});
        this.setState({ quantity: 1 });
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

  updateproductsuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.gtin,
          text: item.productname,
          value: item.productname,
          img: item.productimage,
          imglocal: item.productimagelocal,
        }
      ));
    this.setState({ productsuggests: updatedsuggest });
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

  consumeinventory(gtin,consumeextent){
    console.log('consumeinventory [' + gtin + ']');
    this.setState({ inventoryfetched: false });

    axios.post(this.state.apihost + '/inventory', 
      {
        gtin:gtin,
        retailername:'',
        dateexpiry:'',
        quantity:consumeextent,
        itemstatus:'OUT',
        receiptno:'',
        queryisedible:this.state.queryisedible,
        queryisopened:this.state.queryisopened,
        queryexpirystatus:this.state.queryexpirystatus
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
      if(response.status === 200){
        console.log('consumeinventory [' + response.data[0]['message'] + ']');
        this.setState({ inventorymsg: this.generatecountmsg(response.data[0]['count']) });
        this.setState({ inventoryfetched: true });

        this.setState({ inventory: response.data[0]['results'] });
      }
    })
    .catch(error => {
      if(error.response){
        if(error.response.data){
          console.log('consumeinventory [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
        }
        else{
          console.log('consumeinventory [server unreachable]');
        }
      }
      else{
        console.log('consumeinventory [server unreachable]');
      }
    });    
  }

  clearactionmessage(){
    this.setState({ actionedmsg: '' });
  }

  redirectoproduct(gtin, productname, productimage, productimagelocal, brandname, isedible, isfavourite){
    this.props.history.push({
      pathname: '/product',
      //search: '?isedible=' + this.state.queryisedible + '&isopened=' + this.state.queryisopened,
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
  
  generategriddefault(){
    if(this.state.inventoryfetched){
      return (
        <Card raised key="1">
          <Card.Content>
            <Image rounded
              centered src={this.state.defaultimage}
              floated='right'
              size='tiny'
            />
            <Card.Header className="item title">{this.state.inventorymsg}</Card.Header>
            <Card.Description textAlign="center"></Card.Description>
            <Label className='grey button' attached='top right'>0</Label>
          </Card.Content>
          <Card.Content extra textAlign="center">
            <Modal
              trigger={
                <Button icon onClick={this.clearactionmessage.bind(this)}
                labelPosition='left' className='grey button'>
                  <Icon name='plus' />ADD ITEMS
                </Button>
              }
              closeIcon
              centered={false}
              size="fullscreen"
              dimmer="blurring"
              >
              <Modal.Header>Add items</Modal.Header>
              <Modal.Content image>
                <Image
                  wrapped size='tiny' src={this.state.productimagelocal}
                  onError={(e)=>{e.target.onerror = null; e.target.src=this.state.productimage}}
                />
                <Modal.Description>
                  <Grid columns={1} doubling stackable>
                    <Grid.Column>
                      <label className="fullwidth">Product</label>
                      <Dropdown className="fullwidth" name="productname"
                        search
                        selection
                        noResultsMessage="No product found"
                        value={this.state.productname}
                        options={this.state.productsuggests}
                        onSearchChange={this.lookupproduct.bind(this)}
                        onChange={this.setinventorymetadata.bind(this)}
                      />
                    </Grid.Column>
                    <Grid.Column>
                      <label className="fullwidth">Retailer</label>                    
                      <Dropdown className="fullwidth" name="retailername"
                        search
                        selection
                        allowAdditions
                        noResultsMessage="No retailer found"
                        value={this.state.retailername}
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
                    className='grey button fullwidth' onClick={this.addinventory.bind(this,this.state.gtin)}>
                      ADD
                    </Button>
                  </Grid.Column>
                  <Grid.Column>
                    {this.generateitemadditionmsg()}
                  </Grid.Column>
                </Grid>
              </Modal.Actions>
            </Modal>
          </Card.Content>
        </Card>
      )
    }
    else{
      return ''
    }
  }

  generategriditems(){
    if(!this.state.inventoryfetched){
      return (<Card raised>
                <Message size='tiny'
                  header="Fetching your inventory"
                  content="Please try again later if it doesn't load"
                />
              </Card>
              )
    }
    else{
      return this.state.inventory.map( (item) => (
              <Card raised key={item.gtin}>
                <Card.Content>
                    <Image rounded
                      centered src={item.productimagelocal}
                      floated='right'
                      size='tiny' style={{width: 'auto', height: '70px'}}                      
                      onError={(e)=>{e.target.onerror = null; e.target.src=item.productimage}}
                    />
                  <Card.Header className="item title">{item.productname}</Card.Header>
                  <Card.Meta className="item small">{item.brandname}</Card.Meta>
                  <Card.Description className="item small" textAlign="left">{item.dateexpiry ? 'Best before ' + item.dateexpiry : ''}</Card.Description>
                  <Label className={item.isfavourite === 1 ? 'kuning button' : 'grey button'} attached='top right'>{item.itemcount}</Label>
                </Card.Content>

                <Card.Content extra textAlign="center">
                  <div className='ui three buttons'>
                    <Button icon="edit" className={item.isfavourite === 1 ? 'kuning button' : 'grey button'} onClick={this.redirectoproduct.bind(this,item.gtin,item.productname,item.productimage,item.productimagelocal, item.brandname, item.isedible, item.isfavourite)} />
                    
                    <Modal
                      trigger={<Button icon="minus" className={item.isfavourite === 1 ? 'kuning button' : 'grey button'}
                      onClick={this.clearactionmessage.bind(this)} />}
                      centered={false}
                      size="fullscreen"
                      dimmer="blurring"
                      closeIcon
                    >
                      <Modal.Header>Consume items</Modal.Header>
                      <Modal.Content textAlign='center'>
                        <Button.Group size='massive' vertical>
                          <Button className='grey button' size='massive'
                            onClick={this.consumeinventory.bind(this,item.gtin,0.5)}
                            disabled={item.itemcount % 1 === 0 ? true : false}
                          >
                            CONSUME OPENED ITEM
                          </Button>
                          <Button className='grey button' size='massive'
                            onClick={this.consumeinventory.bind(this,item.gtin,0.5)}
                            disabled={item.itemcount % 1 !== 0 ? true : false}
                          >
                            OPEN NEW ITEM
                          </Button>
                          <Button className='grey button' size='massive'
                            onClick={this.consumeinventory.bind(this,item.gtin,1.0)}
                            disabled={item.itemcount % 1 !== 0 ? true : false}
                          >
                            CONSUME NEW ITEM
                          </Button>
                        </Button.Group>
                      </Modal.Content>
                    </Modal>

                    <Modal
                      trigger={<Button icon="plus" className={item.isfavourite === 1 ? 'kuning button' : 'grey button'}
                      onClick={this.clearactionmessage.bind(this)} />}
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
                            <Button loading={this.state.loading || false} className="fullwidth" color="grey" onClick={this.addinventory.bind(this,item.gtin)}>
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
            ));
    }
  }

  render() {
    return (
      <div
        className={isMobile ? "bodymain mobile" : "bodymain"}
      >
        <Card.Group doubling itemsPerRow={3} stackable>
          {this.generategriddefault()}
          {this.generategriditems()}
        </Card.Group>
      </div>
    )
  }
}
export default Pan3;
