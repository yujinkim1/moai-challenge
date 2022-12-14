import sys
"""
Your $PATH: anaconda3/envs/PATH
"""
__path__ = "Users/PATH"
sys.path.append(__path__)

import os
import argparse

from torch.utils.data import DataLoader
from torchsummary import summary

from util.dataset import CustomDataset
from model import UNet
from train import Trainer

def get_args_parser():
    parser = argparse.ArgumentParser(description='Training', add_help=False)
    
    # save weight folder name
    parser.add_argument('--weight_save_folder_dir', type=str, required=True,
                        help='the path to store weights')
    
    # dataset parameters
    parser.add_argument('--data_dir', type=str, required=True,
                        help='the directory where your dataset is located')
    parser.add_argument('--img_height', type=int, default=512,
                        help='the size of image height')
    parser.add_argument('--img_width', type=int, default=512,
                        help='the size of image width')
    parser.add_argument('--num_classes', type=int, default=3,
                        help='the number of classes in dataset')
    # training parameters
    parser.add_argument('--lr', type=float, default=5e-3,
                        help='learning rate for training')
    parser.add_argument('--end_lr', type=float, default=1e-7,
                        help='the final learning rate value of scheduler')
    parser.add_argument('--optimizer', type=str, default='sgd',
                        help='optimizer (adam or sgd)')
    parser.add_argument('--epochs', type=int, default=100,
                        help='epochs for training')
    parser.add_argument('--ohem_loss_weight', type=float, default=0.5,
                        help='a weight for ohem loss term in total loss function')
    parser.add_argument('--dice_loss_weight', type=float, default=0.5,
                        help='a weight for dice loss term in total loss function')
    parser.add_argument('--separate_out', type=bool, default=True,
                        help='get separated output of combination loss function consist of ohem and dice')
    parser.add_argument('--batch_size', type=int, default=8,
                        help='batch size')
    parser.add_argument('--weight_decay', type=float, default=1e-4,
                        help='weight decay of optimizer SGD')
    parser.add_argument('--lr_scheduling', type=bool, default=True,
                        help='apply learning rate scheduler')
    parser.add_argument('--scheduler_type', type=str, default='polynomial',
                        help='select scheduler type')
    parser.add_argument('--check_point', type=bool, default=True,
                        help='save a weight of model during training when a loss of validating is decreased')
    parser.add_argument('--early_stop', type=bool, default=False,
                        help='the size of image width')
    parser.add_argument('--train_log_step', type=int, default=10,
                        help='print out the logs of training every steps')
    parser.add_argument('--valid_log_step', type=int, default=3,
                        help='print out the logs of validating every steps')
    
    # model parameters
    parser.add_argument('--num_filters', type=int, default=32,
                        help='the number of filters in U-Net')
    parser.add_argument('--pretrained_weight', type=str, default='None',
                        help='Whether to load pretrained weight or not')
    return parser

def main(args):

    train_set = CustomDataset(
        path=args.data_dir, 
        subset='train', 
        transforms_=True, 
        crop_size=(args.img_height, args.img_width),
    )

    train_loader = DataLoader(
        train_set,
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=True,
    )

    valid_set = CustomDataset(
        path=args.data_dir,
        subset='valid',
        transforms_=None,
        crop_size=None,
    )

    valid_loader = DataLoader(
        valid_set,
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=True,
    )

    unet = UNet(num_filters=args.num_filters)
    summary(unet, (1, args.img_height, args.img_width), device='cpu')

    model = Trainer(
        model=unet,
        num_classes=args.num_classes,
        lr=args.lr,
        end_lr=args.end_lr,
        epochs=args.epochs,
        weight_decay=args.weight_decay,
        ohem_loss_weight=args.ohem_loss_weight,
        dice_loss_weight=args.dice_loss_weight,
        separate_out=args.separate_out,
        optimizer=args.optimizer,
        check_point=args.check_point,
        early_stop=args.early_stop,
        lr_scheduling=args.lr_scheduling,
        scheduler_type=args.scheduler_type,
        pretrained_weight=args.pretrained_weight,
        train_log_step=args.train_log_step,
        valid_log_step=args.valid_log_step,
        weight_save_folder_dir=args.weight_save_folder_dir,
    )

    history = model.fit(train_loader, valid_loader)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Model training', parents=[get_args_parser()])
    args = parser.parse_args()
    main(args)
