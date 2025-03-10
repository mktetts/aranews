import { BiArrowFromLeft } from 'react-icons/bi';
import { IMAGES } from '../images';
import { Container, Carousel, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

function Init() {
    const navigate = useNavigate();
    return (
        <div>
            <div className='page-wrapper mt-5'>
                <Container className='neumorphism-container'>
                    <h2 className='mb-5 title'>Welcome to Ara News</h2>
                    <div className='content'>
                        <div className='slogan-container'>
                            <div>
                                <img src={IMAGES.image6} />
                            </div>
                            <div className='slogan'>
                                Boost Engagement, Cut Effort – AI Posting Made Easy!
                            </div>
                            <Button className='mt-3' onClick={() => navigate('/main/chat')}>
                                Enter <BiArrowFromLeft />
                            </Button>
                        </div>
                        <div className='carousel-container'>
                            <Carousel>
                                <Carousel.Item>
                                    <img src={IMAGES.image1} alt='Slide 1' />
                                </Carousel.Item>
                                <Carousel.Item>
                                    <img src={IMAGES.image4} alt='Slide 2' />
                                </Carousel.Item>
                                <Carousel.Item>
                                    <img src={IMAGES.image2} alt='Slide 3' />
                                </Carousel.Item>
                                <Carousel.Item>
                                    <img src={IMAGES.image3} alt='Slide 3' />
                                </Carousel.Item>
                            </Carousel>
                        </div>
                    </div>
                </Container>
            </div>
        </div>
    );
}

export default Init;
