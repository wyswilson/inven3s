import React from "react";
import "./index.css";
import axios from 'axios';
import { getToken } from './utils/common';
import { Message, Container, Grid, Dropdown, Modal, Button, Icon, Input, Label, Card, Image  } from 'semantic-ui-react'
import { DateInput } from 'semantic-ui-calendar-react';
import _ from 'lodash'

class Inventory extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      apihost: 'http://127.0.0.1:8989',
      token: getToken(),
      gtin: '',
      defaultimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      productname: '',
      productimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      brandid:'',
      brandname:'',
      retailerid:'',
      retailername:'',
      inventory:[],
      dateexpiry:'',
      quantity: 1,
      productsuggests: [],
      retailersuggests: [],
      brandsuggests: [],
      modalopen: false,
      loading: false,
      itemaddedmsg: '',
      itemadded: false
    }
  }

  fetchinventory(){
    axios.get(this.state.apihost + '/inventory?isedible=2&ispartiallyconsumed=2&sortby=productname',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        this.setState({ inventory: response.data[0]['results'] });
      }
    })
    .catch(error => {
      if(error.response){
        console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
      }
      else{
        console.log('server unreachable');
      }
    });
  }

  componentDidMount() {
    this.fetchinventory();
  }

  lookupproduct(event, data){
    const gtinorproduct = data.searchQuery

    if(gtinorproduct.length > 3){
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
          this.updateproductsuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        }
        else{
          console.log('server unreachable');
        }
      });
    }
  }

  lookupretailer(event, data){
    const retailer = data.searchQuery

    if(retailer.length > 3){
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
          this.updateretailersuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        }
        else{
          console.log('server unreachable');
        }
      });
    }
  }

  lookupbrand(brand){
    if(brand.length > 3){
      axios.get(this.state.apihost + '/brand/' + brand,
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          this.setState({ brandsuggests: response.data[0]['results'] });
        }
      })
      .catch(error => {
        if(error.response){
          console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        }
        else{
          console.log('server unreachable');
        }
      });
    }
  }

  setinventorymetadata(event, data){
    const field = data.placeholder;
    const value = data.value;
    console.log(field + ':' + value);
    if(field === 'product'){
      const array = this.state.productsuggests;
      let selectedgtin = array.filter(prod => prod.value.includes(value))[0]['key'];
      let selectedimg  = array.filter(prod => prod.value.includes(value))[0]['img'];

      this.setState({ gtin: selectedgtin });
      this.setState({ productname: value });
      this.setState({ productimage: selectedimg });
    }
    else if(field === 'retailer'){
      this.setState({ retailername: value });
    }
    else if(field === 'quantity'){
      this.setState({ quantity: value });
    }
    else if(field === 'expiry'){
      this.setState({ dateexpiry: value });
    }
  }
  
  addinventory(gtin){
    this.setState({ itemaddedmsg: '' });
    this.setState({ itemadded: false });
    this.setState({ loading: true });

    axios.post(this.state.apihost + '/inventory', 
      {
        gtin:gtin,
        retailername:this.state.retailername,
        dateexpiry:this.state.dateexpiry,
        quantity:this.state.quantity,
        itemstatus:'IN',
        receiptno:''
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
        this.setState({ itemaddedmsg: response.data[0]['message'] });
        this.setState({ inventory: response.data[0]['results'] });
        this.setState({ itemadded: true });
        this.setState({ gtin: '' });
        this.setState({ productname: '' });
        this.setState({ productimage: 'https://react.semantic-ui.com/images/wireframe/image.png' });
        this.setState({ retailername: ''});
        this.setState({ dateexpiry: ''});
        this.setState({ quantity: 1 });
      }
    })
    .catch(error => {
      this.setState({ loading: false });
      if(error.response){
        console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        this.setState({ itemaddedmsg: error.response.data[0]['message'] });        
      }
      else{
        console.log('server unreachable');
        this.setState({ itemaddedmsg: 'server unreachable' });
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
        }
      ));
    console.log(updatedsuggest);
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
    console.log(updatedsuggest);
    this.setState({ retailersuggests: updatedsuggest });
  }

  addnewproduct(event,data){
    console.log(data.value);
  }

  addnewretailer(event,data){
    console.log(data.value);
  }

  consumeinventory(gtin){
    console.log(gtin);  
    axios.post(this.state.apihost + '/inventory', 
      {
        gtin:gtin,
        retailername:'',
        dateexpiry:'',
        quantity:0.5,
        itemstatus:'OUT',
        receiptno:''
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
        console.log(response.data[0]['message']);
        this.setState({ inventory: response.data[0]['results'] });
      }
    })
    .catch(error => {
      if(error.response){
        console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        //this.setState({ itemaddedmsg: error.response.data[0]['message'] });        
      }
      else{
        console.log('server unreachable');
        //this.setState({ itemaddedmsg: 'server unreachable' });
      }
    });    
  }
  
  openmodal = () => this.setState({ modalopen: true })
  
  closemodal = () => this.setState({ modalopen: false })

  setdefaultimage(event){
    event.target.src = this.state.defaultimage;
  }

  generateitemadditionmsg(){
      if(this.state.itemaddedmsg !== '' && this.state.itemadded){
        return (
          <Message className="fullwidth" success><Message.Header>{this.state.itemaddedmsg}</Message.Header></Message>
        )
      }
      else if(this.state.itemaddedmsg !== ''){
        return (
          <Message className="fullwidth" negative><Message.Header>{this.state.itemaddedmsg}</Message.Header></Message>        
        )
      }
  }
  
  generategriddefault(){
    if(this.state.inventory.length !== 0){
      
      return (
        <Card raised key="1">
          <Card.Content>
            <Image rounded
              centered src={this.state.defaultimage}
              floated='right'
              size='tiny'
            />
            <Card.Header size='tiny'>Add new item</Card.Header>
            <Card.Meta></Card.Meta>
            <Label color='grey' attached='top right'>0</Label>
          </Card.Content>

          <Card.Content extra textAlign="center">
            <Modal
              trigger={<Button icon="plus" onClick={this.openmodal} />}
              open={this.state.modalopen}
              onClose={this.closemodal} 
              centered={false}
              size="fullscreen"
              dimmer="blurring"
              >
              <Modal.Header>Add item to inventory</Modal.Header>
              <Modal.Content image>
                <Image wrapped size='tiny' src={this.state.productimage} />
                <Modal.Description>
                  <Grid columns={1} doubling stackable>
                    <Grid.Column>
                      <Dropdown className="fullwidth"
                        placeholder="product"
                        search
                        selection
                        allowAdditions
                        value={this.state.productname}
                        options={this.state.productsuggests}
                        additionLabel = "Add new product "
                        onSearchChange={this.lookupproduct.bind(this)}
                        onAddItem={this.addnewproduct.bind(this)}
                        onChange={this.setinventorymetadata.bind(this)}
                      />
                    </Grid.Column>
                    <Grid.Column>
                      <Dropdown className="fullwidth"
                        placeholder="retailer"
                        search
                        selection
                        allowAdditions
                        value={this.state.retailername}
                        options={this.state.retailersuggests}
                        additionLabel = "Add new retailer "
                        onSearchChange={this.lookupretailer.bind(this)}
                        onAddItem={this.addnewretailer.bind(this)}
                        onChange={this.setinventorymetadata.bind(this)}
                      />
                    </Grid.Column>
                    <Grid.Row columns={2}>
                      <Grid.Column>
                        <Input className="fullwidth"
                          placeholder='quantity'
                          value={this.state.quantity}
                          onChange={this.setinventorymetadata.bind(this)}
                        />
                      </Grid.Column>
                      <Grid.Column>
                         <DateInput
                          placeholder="expiry"
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
                    <Button loading={this.state.loading || false} className="fullwidth" color='black' onClick={this.addinventory.bind(this,this.state.gtin)}>
                      <Icon name='checkmark' />add
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
    if(this.state.inventory.length === 0){
      return (<Card raised>
                <Message warning size='tiny'
                  header="Fetching your inventory"
                  content="Please try again later if it doesn't load"
                />
              </Card>
              )
    }
    else{
      return _.map(this.state.inventory, (item) => (
              <Card raised key={item.gtin}>
                <Card.Content>
                  <Image rounded
                    centered src={item.productimage}
                    floated='right'
                    size='tiny'
                    onError={this.setdefaultimage.bind(this)}
                  />
                  <Card.Header size='tiny'>{item.productname}</Card.Header>
                  <Card.Meta>{item.brandname}</Card.Meta>
                  <Label color='grey' attached='top right'>{item.itemcount}</Label>
                </Card.Content>

                <Card.Content extra textAlign="center">
                  <div className='ui three buttons'>
                    <Modal
                      trigger={<Button icon="edit" />}
                      centered={false}
                      size="fullscreen"
                      dimmer="blurring"
                    >
                      <Modal.Header>Edit product and brand</Modal.Header>
                      <Modal.Content image>
                        <Image wrapped size='tiny' src={item.productimage} />
                        <Modal.Description>
                          <Grid columns={1} doubling stackable>
                            <Grid.Column>
                              {item.productname}
                              <Input className="fullwidth" onChange={e => this.setState({ gtin:item.gtin, productname: e.target.value })}/>
                            </Grid.Column>
                            <Grid.Column>
                              {item.productimage}
                              <Input className="fullwidth" onChange={e => this.setState({ gtin:item.gtin, productimage: e.target.value })}/>
                            </Grid.Column>
                            <Grid.Column>
                              {item.brandname}
                            </Grid.Column>
                          </Grid>
                        </Modal.Description>
                      </Modal.Content>
                      <Modal.Actions>
                        <Button color="black" className="fullwidth">save</Button>
                      </Modal.Actions>
                    </Modal>
                    <Button icon="minus" onClick={this.consumeinventory.bind(this,item.gtin)}/>
                    <Modal
                      trigger={<Button icon="plus" />}
                      centered={false}
                      size="fullscreen"
                      dimmer="blurring"
                    >
                      <Modal.Header>Specify retailer, quantity and expiry</Modal.Header>
                      <Modal.Content image>
                        <Image wrapped size='tiny' src={item.productimage} />
                        <Modal.Description>
                          <Grid columns={1} doubling stackable>
                            <Grid.Column>
                              <Dropdown className="fullwidth"
                                placeholder="retailer"
                                search
                                selection
                                allowAdditions
                                value={this.state.retailername}
                                options={this.state.retailersuggests}
                                additionLabel = "Add new retailer "
                                onSearchChange={this.lookupretailer.bind(this)}
                                onAddItem={this.addnewretailer.bind(this)}
                                onChange={this.setinventorymetadata.bind(this)}
                              />
                            </Grid.Column>
                            <Grid.Column>
                              <Input className="fullwidth"
                                placeholder='quantity'
                                value={this.state.quantity}
                                onChange={this.setinventorymetadata.bind(this)}
                              />
                            </Grid.Column>
                            <Grid.Column>
                               <DateInput
                                placeholder="expiry"
                                dateFormat="YYYY-MM-DD"
                                value={this.state.dateexpiry}
                                onChange={this.setinventorymetadata.bind(this)}
                              />
                            </Grid.Column>                      
                          </Grid>
                        </Modal.Description>
                      </Modal.Content>
                      <Modal.Actions>
                        <Grid columns={2} container doubling stackable>
                          <Grid.Column>
                            <Button loading={this.state.loading || false} className="fullwidth" color="black" onClick={this.addinventory.bind(this,item.gtin)}>
                              <Icon name='checkmark' />add
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
            ))
    }
  }

  render() {
    return (
      <Container fluid>
        <Card.Group doubling itemsPerRow={6} stackable>
          {this.generategriddefault()}
          {this.generategriditems()}
        </Card.Group>
      </Container>
    )
  }
}
export default Inventory;
